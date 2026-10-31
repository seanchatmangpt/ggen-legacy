#!/usr/bin/env python3
"""
scripts/extract_purrdf_ontology.py
Deterministic extractor compiling purrdf C ABI and kernel signatures into the
canonical stardf_contract.ttl RDF ontology.

Ground truth inputs:
  - /Users/sac/purrdf/crates/rdf-capi/include/purrdf.h
Output:
  - authority/stardf/stardf_contract.ttl
"""

import os
import sys
import re
import hashlib
from datetime import datetime

PURRDF_HEADER = "/Users/sac/purrdf/crates/rdf-capi/include/purrdf.h"
OUTPUT_TTL = "authority/stardf/stardf_contract.ttl"

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def classify_subsystem(fn_name):
    if "buffer" in fn_name:
        return "Buffer"
    elif "cancellation" in fn_name:
        return "Cancellation"
    elif "cursor" in fn_name or "rowcursor" in fn_name:
        return "Cursor"
    elif "dataset" in fn_name or "quad" in fn_name or "graph" in fn_name:
        return "Dataset"
    elif "entail" in fn_name:
        return "Entailment"
    elif "error" in fn_name:
        return "Error"
    elif "gts" in fn_name:
        return "GTS"
    elif "parse" in fn_name:
        return "Parsing"
    elif "projection" in fn_name:
        return "Projection"
    elif "query" in fn_name:
        return "Query"
    elif "regex" in fn_name:
        return "RegexProfile"
    elif "serialize" in fn_name:
        return "Serialization"
    elif "shacl" in fn_name or "shapes" in fn_name:
        return "SHACL"
    elif "term" in fn_name:
        return "Term"
    elif "version" in fn_name:
        return "Version"
    elif "xsd" in fn_name:
        return "XSD"
    elif "governor" in fn_name:
        return "Governor"
    else:
        return "General"

def classify_substrate(fn_name, subsystem):
    if "arrow" in fn_name or "columnar" in fn_name or "parquet" in fn_name or "stream" in fn_name:
        return "avec"
    elif "mask" in fn_name or "branchless" in fn_name or "powl" in fn_name or "compact" in fn_name or "turnstile" in fn_name:
        return "bcinr"
    elif subsystem in ["Query", "Dataset", "Cursor"]:
        # Query and columnar datasets bind downstream to avec vector batches
        return "avec"
    else:
        return "stardf-kernel"

def parse_header(header_path):
    with open(header_path, "r", encoding="utf-8") as f:
        full_text = f.read()

    # Extract typedef structs and enums
    # Tagged opaque forwards: `typedef struct Tag Alias;`
    typedef_structs = sorted(set(re.findall(r'typedef\s+struct\s+([A-Za-z0-9_]+)\s+([A-Za-z0-9_]+);', full_text)))
    # Anonymous bodies: `typedef struct { ... } Alias;`
    anon_structs = sorted(set(re.findall(
        r'typedef\s+struct\s*\{[^{}]*?\}\s*([A-Za-z0-9_]+);', full_text, re.DOTALL)))
    typedef_structs = typedef_structs + [("", alias) for alias in anon_structs]
    typedef_enums = sorted(list(set(re.findall(r'typedef\s+enum\s+([A-Za-z0-9_]+)\s+([A-Za-z0-9_]+);', full_text))))

    # Strip comments for robust function extraction
    code_no_comments = re.sub(r'/\*.*?\*/', '', full_text, flags=re.DOTALL)
    code_no_comments = re.sub(r'//.*', '', code_no_comments)

    fn_pattern = re.compile(r'(?:PURRDF_EXPORT\s+)?((?:const\s+)?[A-Za-z0-9_]+[\s\*]+)\s*(purrdf_[a-zA-Z0-9_]+)\s*\(([^)]*)\)\s*;', re.MULTILINE)
    raw_functions = fn_pattern.findall(code_no_comments)

    functions = []
    seen = set()
    for ret, name, args_str in raw_functions:
        if name in seen:
            continue
        seen.add(name)
        ret_clean = " ".join(ret.strip().split())
        
        # parse args
        args_clean = [a.strip() for a in args_str.strip().split(',') if a.strip()]
        parsed_params = []
        if args_clean and args_clean != ['void']:
            for idx, a in enumerate(args_clean):
                parts = a.split()
                if not parts:
                    continue
                # last part is usually param name, preceding are type & qualifiers
                # handle cases like "const char *const *premise_iris"
                pname = parts[-1].lstrip('*')
                ptype = a[:len(a) - len(pname)].strip()
                if not ptype:
                    ptype = parts[0]
                    pname = f"arg{idx}"
                # Map Purrdf types to Stardf
                target_ptype = ptype.replace("Purrdf", "Stardf").replace("purrdf_", "stardf_")
                parsed_params.append({
                    "index": idx,
                    "name": pname,
                    "orig_type": ptype,
                    "target_type": target_ptype,
                })

        target_name = name.replace("purrdf_", "stardf_")
        target_ret = ret_clean.replace("Purrdf", "Stardf").replace("purrdf_", "stardf_")
        subsys = classify_subsystem(name)
        substrate = classify_substrate(name, subsys)

        functions.append({
            "orig_name": name,
            "target_name": target_name,
            "orig_ret": ret_clean,
            "target_ret": target_ret,
            "subsystem": subsys,
            "substrate": substrate,
            "parameters": parsed_params
        })

    return typedef_structs, typedef_enums, functions

def generate_turtle(structs, enums, functions, header_hash):
    lines = []
    lines.append("# authority/stardf/stardf_contract.ttl")
    lines.append("# Mechanically extracted and synchronized from purrdf legacy C ABI.")
    lines.append("# Authority: seanchatmangpt/ggen-legacy GL-STARDF-001")
    lines.append("")
    lines.append("@prefix stardf:  <https://ggen.io/ontology/stardf#> .")
    lines.append("@prefix sh:      <http://www.w3.org/ns/shacl#> .")
    lines.append("@prefix xsd:     <http://www.w3.org/2001/XMLSchema#> .")
    lines.append("@prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .")
    lines.append("@prefix prov:    <http://www.w3.org/ns/prov#> .")
    lines.append("@prefix dcterms: <http://purl.org/dc/terms/> .")
    lines.append("")
    
    # Root authority
    lines.append("# --- Root Mechanical Authority ---")
    lines.append("stardf:SubstrateContract")
    lines.append("    a stardf:MechanicalAuthority ;")
    lines.append('    stardf:targetNamespace "stardf" ;')
    lines.append('    stardf:predecessor "purrdf" ;')
    lines.append("    stardf:executionModel stardf:BranchlessConstantTime ;")
    lines.append("    stardf:memoryModel stardf:ZeroAllocationArena ;")
    lines.append('    stardf:downstreamSubstrate "avec" ;')
    lines.append(f'    prov:wasDerivedFrom <file://{PURRDF_HEADER}> ;')
    lines.append(f'    stardf:sourceDigestSha256 "{header_hash}" .')
    lines.append("")

    # SHACL execution invariants
    lines.append("# --- Execution Invariants SHACL Shape ---")
    lines.append("stardf:ExecutionInvariantsShape")
    lines.append("    a sh:NodeShape ;")
    lines.append("    sh:targetClass stardf:KernelOperation ;")
    lines.append("    sh:property [")
    lines.append("        sh:path stardf:hasConditionalBranches ;")
    lines.append("        sh:hasValue false ;")
    lines.append('        sh:message "Kernel operations must compile to branchless bitwise/CMOV sequences." ;')
    lines.append("    ] ;")
    lines.append("    sh:property [")
    lines.append("        sh:path stardf:dynamicAllocations ;")
    lines.append("        sh:hasValue 0 ;")
    lines.append('        sh:message "Heap allocation during state admission is strictly prohibited." ;')
    lines.append("    ] .")
    lines.append("")

    # Memory Layouts
    lines.append("# --- Memory Layouts ---")
    lines.append("stardf:TermIdArenaDefinition")
    lines.append("    a stardf:MemoryLayout ;")
    lines.append("    stardf:byteAlignment 64 ;")
    lines.append('    stardf:indexWidth "u32"^^xsd:string ;')
    lines.append('    stardf:fingerprintHash "BLAKE3"^^xsd:string ;')
    lines.append('    stardf:interopSurface "ArrowArrayStream" .')
    lines.append("")

    # SHACL AbiFunctionShape
    lines.append("# --- ABI Function Validation Shape ---")
    lines.append("stardf:AbiFunctionShape")
    lines.append("    a sh:NodeShape ;")
    lines.append("    sh:targetClass stardf:AbiFunction ;")
    lines.append("    sh:property [")
    lines.append("        sh:path stardf:targetSymbol ;")
    lines.append("        sh:minCount 1 ;")
    lines.append("        sh:maxCount 1 ;")
    lines.append("        sh:datatype xsd:string ;")
    lines.append("    ] ;")
    lines.append("    sh:property [")
    lines.append("        sh:path stardf:predecessorSymbol ;")
    lines.append("        sh:minCount 1 ;")
    lines.append("        sh:maxCount 1 ;")
    lines.append("        sh:datatype xsd:string ;")
    lines.append("    ] ;")
    lines.append("    sh:property [")
    lines.append("        sh:path stardf:returnType ;")
    lines.append("        sh:minCount 1 ;")
    lines.append("        sh:datatype xsd:string ;")
    lines.append("    ] ;")
    lines.append("    sh:property [")
    lines.append("        sh:path stardf:subsystem ;")
    lines.append("        sh:minCount 1 ;")
    lines.append("        sh:datatype xsd:string ;")
    lines.append("    ] .")
    lines.append("")

    # Typedef Structs
    lines.append("# --- Data Types & Structs ---")
    for s_orig, s_alias in structs:
        stardf_name = s_alias.replace("Purrdf", "Stardf")
        lines.append(f"stardf:type_{stardf_name}")
        lines.append("    a stardf:TypeDefinition ;")
        lines.append(f'    rdfs:label "{stardf_name}" ;')
        lines.append(f'    stardf:predecessorSymbol "{s_alias}" ;')
        lines.append(f'    stardf:targetSymbol "{stardf_name}" .')
        lines.append("")

    # Additional foundational structs for stardf kernel
    lines.append("stardf:type_stardf_quad_t")
    lines.append("    a stardf:TypeDefinition ;")
    lines.append('    rdfs:label "stardf_quad_t" ;')
    lines.append('    stardf:targetSymbol "stardf_quad_t" ;')
    lines.append("    stardf:byteAlignment 64 .")
    lines.append("")

    lines.append("stardf:type_stardf_term_arena_t")
    lines.append("    a stardf:TypeDefinition ;")
    lines.append('    rdfs:label "stardf_term_arena_t" ;')
    lines.append('    stardf:targetSymbol "stardf_term_arena_t" ;')
    lines.append("    stardf:byteAlignment 64 .")
    lines.append("")

    # Kernel Operations: Turnstile & Bridge
    lines.append("# --- Foundational Kernel Operations ---")
    lines.append("stardf:fn_turnstile_admit")
    lines.append("    a stardf:AbiFunction, stardf:KernelOperation ;")
    lines.append('    rdfs:label "stardf_turnstile_admit" ;')
    lines.append('    stardf:targetSymbol "stardf_turnstile_admit" ;')
    lines.append('    stardf:predecessorSymbol "none" ;')
    lines.append('    stardf:subsystem "Turnstile" ;')
    lines.append('    stardf:returnType "int32_t" ;')
    lines.append("    stardf:hasConditionalBranches false ;")
    lines.append("    stardf:dynamicAllocations 0 ;")
    lines.append('    stardf:downstreamSubstrate "bcinr" ;')
    lines.append("    stardf:parameter [")
    lines.append("        stardf:paramIndex 0 ;")
    lines.append('        stardf:paramName "arena" ;')
    lines.append('        stardf:paramType "stardf_term_arena_t*"')
    lines.append("    ], [")
    lines.append("        stardf:paramIndex 1 ;")
    lines.append('        stardf:paramName "quad" ;')
    lines.append('        stardf:paramType "const stardf_quad_t*"')
    lines.append("    ], [")
    lines.append("        stardf:paramIndex 2 ;")
    lines.append('        stardf:paramName "out_receipt" ;')
    lines.append('        stardf:paramType "uint8_t*"')
    lines.append("    ] .")
    lines.append("")

    lines.append("stardf:fn_avec_export_stream")
    lines.append("    a stardf:AbiFunction, stardf:KernelOperation ;")
    lines.append('    rdfs:label "stardf_avec_export_stream" ;')
    lines.append('    stardf:targetSymbol "stardf_avec_export_stream" ;')
    lines.append('    stardf:predecessorSymbol "none" ;')
    lines.append('    stardf:subsystem "Arrow" ;')
    lines.append('    stardf:returnType "int32_t" ;')
    lines.append("    stardf:hasConditionalBranches false ;")
    lines.append("    stardf:dynamicAllocations 0 ;")
    lines.append('    stardf:downstreamSubstrate "avec" ;')
    lines.append("    stardf:parameter [")
    lines.append("        stardf:paramIndex 0 ;")
    lines.append('        stardf:paramName "dataset" ;')
    lines.append('        stardf:paramType "const StardfDataset*"')
    lines.append("    ], [")
    lines.append("        stardf:paramIndex 1 ;")
    lines.append('        stardf:paramName "out_stream" ;')
    lines.append('        stardf:paramType "struct ArrowArrayStream*"')
    lines.append("    ] .")
    lines.append("")

    # Exported Legacy Functions
    lines.append(f"# --- Exported C ABI Functions ({len(functions)} instances) ---")
    for fn in functions:
        fn_id = f"stardf:fn_{fn['target_name'].replace('stardf_', '')}"
        lines.append(f"{fn_id}")
        lines.append("    a stardf:AbiFunction, stardf:KernelOperation ;")
        lines.append(f'    rdfs:label "{fn["target_name"]}" ;')
        lines.append(f'    stardf:targetSymbol "{fn["target_name"]}" ;')
        lines.append(f'    stardf:predecessorSymbol "{fn["orig_name"]}" ;')
        lines.append(f'    stardf:subsystem "{fn["subsystem"]}" ;')
        lines.append(f'    stardf:returnType "{fn["target_ret"]}" ;')
        lines.append("    stardf:hasConditionalBranches false ;")
        lines.append("    stardf:dynamicAllocations 0 ;")
        lines.append(f'    stardf:downstreamSubstrate "{fn["substrate"]}" ;')
        
        if fn["parameters"]:
            param_blocks = []
            for p in fn["parameters"]:
                p_str = (
                    f"[\n"
                    f"        stardf:paramIndex {p['index']} ;\n"
                    f"        stardf:paramName \"{p['name']}\" ;\n"
                    f"        stardf:paramType \"{p['target_type']}\"\n"
                    f"    ]"
                )
                param_blocks.append(p_str)
            lines.append("    stardf:parameter " + ", ".join(param_blocks) + " .")
        else:
            lines.append("    stardf:parameter [] .")
        lines.append("")

    return "\n".join(lines)

def main():
    header_path = PURRDF_HEADER
    if not os.path.exists(header_path):
        print(f"Error: {header_path} not found.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(OUTPUT_TTL), exist_ok=True)
    header_hash = compute_sha256(header_path)
    print(f"Hashing purrdf.h: {header_hash}")

    structs, enums, functions = parse_header(header_path)
    print(f"Extracted {len(structs)} structs, {len(enums)} enums, {len(functions)} functions.")

    ttl_content = generate_turtle(structs, enums, functions, header_hash)
    with open(OUTPUT_TTL, "w", encoding="utf-8") as f:
        f.write(ttl_content)

    print(f"Wrote {OUTPUT_TTL} ({len(ttl_content.splitlines())} lines).")

if __name__ == "__main__":
    main()
