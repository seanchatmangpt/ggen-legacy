//! stardf-arrow-capi: C ABI membrane crate (cdylib + rlib) for the stardf
//! Arrow substrate. Modeled on avec-ffi's export style; all state crosses the
//! membrane as opaque handles owned by the caller.
//!
//! Status codes follow the purrdf purrdf.h convention: OK=0, NULL_POINTER=1,
//! INVALID_ARGUMENT=3, ARENA_FULL=16.
//!
//! Lanes: this file is lane 7's. `term.rs` and `stream_c.rs` are lane 8/9's
//! and currently carry lane-7 minimal fallbacks (see their headers) that may
//! be replaced wholesale without touching lib.rs.

#![allow(clippy::missing_safety_doc)]

pub mod ownership; // LANE 10: court-facing detection hook (tag_mint/tag_claim/pending)
mod stream_c;
mod term;

pub use avec_arrow::c_abi::{ArrowArray, ArrowSchema}; // LANE 10 (disclosed): FFI struct types for the court tests
pub use stream_c::{export_stream, stream_free, ArrowArrayStream};
pub use stream_c::{stream_get_next_shim, stream_get_schema_shim}; // LANE 10 (disclosed): court consume shims
pub use term::StardfArena;

use core::ffi::c_char;
use std::sync::Mutex;
use std::vec::Vec;

/// Version string served by stardf_arrow_version, NUL-terminated.
pub const VERSION_C: &[u8] = b"26.9.29\0";

/// OK.
pub const STATUS_OK: i32 = 0;
/// A required pointer argument was null.
pub const STATUS_NULL_POINTER: i32 = 1;
/// A value argument was out of range (0-capacity, unknown term id, ...).
pub const STATUS_INVALID_ARGUMENT: i32 = 3;
/// The arena byte budget was exhausted.
pub const STATUS_ARENA_FULL: i32 = 16;

/// Last error message served by stardf_last_error. Stored under a mutex so
/// the served pointer stays valid until the next failing call overwrites it.
static LAST_ERROR: Mutex<Option<Vec<u8>>> = Mutex::new(None);

fn set_last_error(msg: &'static [u8]) {
    if let Ok(mut slot) = LAST_ERROR.lock() {
        *slot = Some(msg.to_vec());
    }
}

/// stardf_last_error() - message for the most recent failing call, valid
/// until the next failing call on this crate.
#[unsafe(no_mangle)]
pub extern "C" fn stardf_last_error() -> *const c_char {
    match LAST_ERROR.lock() {
        Ok(slot) => match slot.as_ref() {
            Some(bytes) => bytes.as_ptr() as *const c_char,
            None => core::ptr::null(),
        },
        Err(_) => core::ptr::null(),
    }
}

/// stardf_arrow_version() - NUL-terminated version string pointer.
#[unsafe(no_mangle)]
pub extern "C" fn stardf_arrow_version() -> *const c_char {
    VERSION_C.as_ptr() as *const c_char
}

/// stardf_arena_new(capacity_bytes) - allocate a term arena with a total
/// byte budget. Returns NULL on capacity_bytes == 0 (INVALID_ARGUMENT).
///
/// # Safety
/// Plain allocation; no pointer argument is dereferenced.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn stardf_arena_new(capacity_bytes: usize) -> *mut StardfArena {
    match StardfArena::with_capacity_bytes(capacity_bytes) {
        Some(a) => Box::into_raw(Box::new(a)),
        None => {
            set_last_error(b"stardf_arena_new: capacity_bytes must be > 0");
            core::ptr::null_mut()
        }
    }
}

/// stardf_arena_intern(arena, lexical, len) - intern a lexical term,
/// returning its stable id (ids start at 1). Returns 0 (the reserved null
/// term id) and sets the last error on NULL_POINTER / INVALID_ARGUMENT /
/// ARENA_FULL.
///
/// # Safety
/// lexical must point at len readable bytes.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn stardf_arena_intern(
    arena: *mut StardfArena, lexical: *const u8, len: usize,
) -> u32 {
    if arena.is_null() || lexical.is_null() {
        set_last_error(b"stardf_arena_intern: null arena or lexical pointer");
        return 0;
    }
    if len == 0 {
        set_last_error(b"stardf_arena_intern: len must be > 0");
        return 0;
    }
    let bytes: &[u8] = std::slice::from_raw_parts(lexical, len);
    match (*arena).intern(bytes) {
        Some(id) => id,
        None => {
            set_last_error(b"stardf_arena_intern: arena budget exhausted");
            0
        }
    }
}

/// stardf_arena_free(arena) - free an arena from stardf_arena_new. Typed
/// no-op on null.
///
/// # Safety
/// arena must be null or a live stardf_arena_new handle, freed exactly once.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn stardf_arena_free(arena: *mut StardfArena) {
    if arena.is_null() {
        return;
    }
    drop(Box::from_raw(arena));
}

/// Append-only quad batch. Owned by the caller via stardf_batch_append_quad;
/// the lexical forms live in the arena, the batch carries term ids only.
pub struct StardfBatch {
    /// Quads as (s, p, o, g) term-id rows.
    pub quads: std::vec::Vec<[u32; 4]>,
}

impl StardfBatch {
    /// New empty batch.
    pub fn new() -> Self {
        Self {
            quads: std::vec::Vec::new(),
        }
    }
}

impl Default for StardfBatch {
    fn default() -> Self {
        Self::new()
    }
}

/// stardf_batch_append_quad(arena, s, p, o, g) - append one quad of term ids
/// to the arena's batch, creating it on first call; returns the batch handle
/// (stable for the arena's lifetime) or NULL with last-error set.
///
/// # Safety
/// arena must be a live stardf_arena_new handle or null.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn stardf_batch_append_quad(
    arena: *mut StardfArena, s: u32, p: u32, o: u32, g: u32,
) -> *mut StardfBatch {
    if arena.is_null() {
        set_last_error(b"stardf_batch_append_quad: null arena");
        return core::ptr::null_mut();
    }
    let n = (*arena).len();
    for id in [s, p, o, g] {
        if id == 0 || id > n {
            set_last_error(b"stardf_batch_append_quad: term id out of range");
            return core::ptr::null_mut();
        }
    }
    if !(*arena).charge_quad() {
        set_last_error(b"stardf_batch_append_quad: arena budget exhausted");
        return core::ptr::null_mut();
    }
    (*arena).batch_mut().quads.push([s, p, o, g]);
    (*arena).batch_mut() as *mut StardfBatch
}

/// stardf_avec_export_stream(batch, out_stream) - export the batch as an
/// owned ArrowArrayStream (authority/stardf/stardf_contract.ttl
/// fn_avec_export_stream seam, downstreamSubstrate avec). Returns STATUS_OK
/// and stores the stream into out_stream on success.
///
/// # Safety
/// batch must be a live batch handle or null; out_stream must be a valid
/// writable slot.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn stardf_avec_export_stream(
    batch: *mut StardfBatch, out_stream: *mut *mut ArrowArrayStream,
) -> i32 {
    if batch.is_null() || out_stream.is_null() {
        set_last_error(b"stardf_avec_export_stream: null batch or out_stream");
        return STATUS_NULL_POINTER;
    }
    *out_stream = export_stream(&*batch);
    STATUS_OK
}

/// stardf_stream_free(stream) - free a stream from
/// stardf_avec_export_stream. Typed no-op on null.
///
/// # Safety
/// stream must be null or a live stream handle, freed exactly once.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn stardf_stream_free(stream: *mut ArrowArrayStream) {
    stream_free(stream);
}

// ---------------------------------------------------------------------------
// Release-tagged export surface (allocation-identity lifecycle; court:
// tests/alloc_identity.rs, court: tests/cross_allocator_court.rs)
// ---------------------------------------------------------------------------

use avec_arrow::c_abi::export; // ArrowArray/ArrowSchema imported at line 19 (lane 10 disclosed); compile-freeze unblock by lane 11
use core::sync::atomic::{AtomicI64, AtomicPtr, AtomicUsize, Ordering};

/// Live export slots read by the foreign importer.
static ARRAY_SLOT: AtomicPtr<ArrowArray> = AtomicPtr::new(core::ptr::null_mut());
static SCHEMA_SLOT: AtomicPtr<ArrowSchema> = AtomicPtr::new(core::ptr::null_mut());
static ROWS: AtomicI64 = AtomicI64::new(0);

/// Unclaimed ownership tags: +1 per mint, -1 per honest release. The mutant
/// feature routes release through the untagged foreign path, leaving the
/// tag pending (the leak the cross-allocator court detects).
static PENDING_TAGS: AtomicUsize = AtomicUsize::new(0);

/// Outcome of [`stardf_release`].
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
#[repr(i32)]
pub enum ReleaseOutcome {
    /// Freed through stardf's tagged release chain.
    Released,
    /// Freed (leaked) through the untagged foreign path (mutant only).
    ReleasedViaForeign,
}

/// stardf_i32_batch(n, null_every) - mint an i32 primitive batch (null at
/// every `null_every`-th lane when > 0) and export it into the live slots.
/// Returns the live ArrowArray pointer (zero-copy identity with
/// stardf_array_addr).
///
/// # Safety
/// Plain allocation; export slots are process-global.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn stardf_i32_batch(n: i64, null_every: i64) -> *mut ArrowArray {
    let mut b = avec_arrow::primitive::PrimitiveBuilder::<i32>::new();
    let mut i = 0;
    while i < n {
        if null_every > 0 && i % null_every == null_every - 1 {
            b.push(None);
        } else {
            b.push(Some(i as i32));
        }
        i += 1;
    }
    let (array, schema) = export(b.finish(), c"i".as_ptr());
    ROWS.store(n, Ordering::Relaxed);
    ARRAY_SLOT.store(Box::leak(Box::new(array)), Ordering::Relaxed);
    SCHEMA_SLOT.store(Box::leak(Box::new(schema)), Ordering::Relaxed);
    PENDING_TAGS.fetch_add(1, Ordering::AcqRel);
    ARRAY_SLOT.load(Ordering::Relaxed)
}

/// stardf_array_addr() - address of the live exported array slot.
#[unsafe(no_mangle)]
pub extern "C" fn stardf_array_addr() -> usize {
    ARRAY_SLOT.load(Ordering::Relaxed) as usize
}

/// stardf_batch_rows() - length of the last exported batch.
#[unsafe(no_mangle)]
pub extern "C" fn stardf_batch_rows() -> i64 {
    ROWS.load(Ordering::Relaxed)
}

/// stardf_pending_tags() - unclaimed ownership tags.
#[unsafe(no_mangle)]
pub extern "C" fn stardf_pending_tags() -> usize {
    PENDING_TAGS.load(Ordering::Acquire)
}

/// stardf_release(array) - release a stardf-owned export through the tagged
/// chain (array + schema release callbacks; both drop inside stardf's
/// allocator). Under the `mutant-cross-alloc` feature this routes through
/// the untagged foreign path instead (leak; the positive control the
/// cross-allocator court flips on).
///
/// # Safety
/// `array` must be the live stardf-owned export from stardf_i32_batch,
/// released exactly once.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn stardf_release(array: *mut ArrowArray) -> ReleaseOutcome {
    if array.is_null() {
        set_last_error(b"stardf_release: null array");
        // A null release claims nothing; surfaced via last-error, typed here
        // as the foreign path (nothing stardf-owned was freed).
        return ReleaseOutcome::ReleasedViaForeign;
    }
    #[cfg(feature = "mutant-cross-alloc")]
    {
        // MUTANT: untagged foreign free — no release callbacks, no tag
        // claim; the export leaks and the identity delta stays open.
        let _ = array;
        return ReleaseOutcome::ReleasedViaForeign;
    }
    #[cfg(not(feature = "mutant-cross-alloc"))]
    {
        if let Some(release) = (*array).release.take() {
            release(array);
        }
        let schema = SCHEMA_SLOT.swap(core::ptr::null_mut(), Ordering::AcqRel);
        if !schema.is_null() {
            if let Some(release) = (*schema).release.take() {
                release(schema);
            }
        }
        ARRAY_SLOT.store(core::ptr::null_mut(), Ordering::Relaxed);
        PENDING_TAGS.fetch_sub(1, Ordering::AcqRel);
        ReleaseOutcome::Released
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use core::ffi::CStr;

    fn cstr(p: *const c_char) -> &'static str {
        unsafe { CStr::from_ptr(p) }.to_str().unwrap()
    }

    #[test]
    fn version_is_nul_terminated_26_9_29() {
        assert_eq!(cstr(stardf_arrow_version()), "26.9.29");
    }

    #[test]
    fn arena_new_rejects_zero_capacity() {
        assert!(unsafe { stardf_arena_new(0) }.is_null());
        assert_eq!(
            cstr(stardf_last_error()),
            "stardf_arena_new: capacity_bytes must be > 0"
        );
    }

    #[test]
    fn intern_round_trips_and_dedups() {
        let arena = unsafe { stardf_arena_new(1 << 16) };
        let lex = b"ex:s\0";
        let a = unsafe { stardf_arena_intern(arena, lex.as_ptr(), 4) };
        let b = unsafe { stardf_arena_intern(arena, lex.as_ptr(), 4) };
        assert_eq!(a, b);
        assert_ne!(a, 0);
        unsafe { stardf_arena_free(arena) };
    }

    #[test]
    fn intern_null_pointer_and_len_guards() {
        assert_eq!(
            unsafe { stardf_arena_intern(core::ptr::null_mut(), c"x".as_ptr().cast::<u8>(), 1) },
            0
        );
        let arena = unsafe { stardf_arena_new(1 << 16) };
        assert_eq!(
            unsafe { stardf_arena_intern(arena, core::ptr::null(), 1) },
            0
        );
        assert_eq!(
            unsafe { stardf_arena_intern(arena, c"x".as_ptr().cast::<u8>(), 0) },
            0
        );
        unsafe { stardf_arena_free(arena) };
    }

    #[test]
    fn intern_reports_arena_full() {
        let arena = unsafe { stardf_arena_new(term::TERM_OVERHEAD + 3) };
        let ok = unsafe { stardf_arena_intern(arena, b"abc".as_ptr(), 3) };
        assert_ne!(ok, 0);
        assert_eq!(
            unsafe { stardf_arena_intern(arena, b"toolong".as_ptr(), 7) },
            0
        );
        assert_eq!(
            cstr(stardf_last_error()),
            "stardf_arena_intern: arena budget exhausted"
        );
        unsafe { stardf_arena_free(arena) };
    }

    #[test]
    fn append_validates_term_ids_and_exports_stream() {
        let arena = unsafe { stardf_arena_new(1 << 16) };
        let s = unsafe { stardf_arena_intern(arena, b"a".as_ptr(), 1) };
        let p = unsafe { stardf_arena_intern(arena, b"b".as_ptr(), 1) };
        let o = unsafe { stardf_arena_intern(arena, b"c".as_ptr(), 1) };
        let g = unsafe { stardf_arena_intern(arena, b"d".as_ptr(), 1) };
        let batch = unsafe { stardf_batch_append_quad(arena, s, p, o, g) };
        assert!(!batch.is_null());
        // Unknown / zero term id refused.
        assert!(unsafe { stardf_batch_append_quad(arena, s, p, o, 0) }.is_null());
        assert!(unsafe { stardf_batch_append_quad(arena, s, p, o, 99) }.is_null());
        assert!(unsafe { stardf_batch_append_quad(core::ptr::null_mut(), s, p, o, g) }.is_null());

        let mut stream: *mut ArrowArrayStream = core::ptr::null_mut();
        let status = unsafe { stardf_avec_export_stream(batch, &mut stream) };
        assert_eq!(status, STATUS_OK);
        assert!(!stream.is_null());

        // Read the stream back through the C Stream Interface callbacks.
        unsafe {
            let mut schema: avec_arrow::c_abi::ArrowSchema = core::mem::zeroed();
            assert_eq!(stream_c::stream_get_schema_shim(stream, &mut schema), 0);
            let mut array: avec_arrow::c_abi::ArrowArray = core::mem::zeroed();
            assert_eq!(stream_c::stream_get_next_shim(stream, &mut array), 0);
            assert_eq!(array.length, 1); // one Quad64 row -> one yielded batch
            let mut eos: avec_arrow::c_abi::ArrowArray = core::mem::zeroed();
            assert_eq!(stream_c::stream_get_next_shim(stream, &mut eos), 0);
            assert_eq!(eos.length, 0); // end of stream

            // Release chain: stream release drops the exported pair, then
            // stardf_stream_free is a typed no-op on the released stream.
            if let Some(release) = (*stream).release {
                release(stream);
            }
            stardf_stream_free(stream);
        }
        unsafe { stardf_arena_free(arena) };
    }

    #[test]
    fn export_stream_null_arguments() {
        let mut slot: *mut ArrowArrayStream = core::ptr::null_mut();
        assert_eq!(
            unsafe { stardf_avec_export_stream(core::ptr::null_mut(), &mut slot) },
            STATUS_NULL_POINTER
        );
        assert_eq!(
            unsafe {
                stardf_avec_export_stream(
                    std::ptr::dangling_mut::<StardfBatch>(),
                    core::ptr::null_mut(),
                )
            },
            STATUS_NULL_POINTER
        );
    }

    #[test]
    fn frees_are_typed_noops_on_null() {
        unsafe {
            stardf_arena_free(core::ptr::null_mut());
            stardf_stream_free(core::ptr::null_mut());
        }
    }
}
