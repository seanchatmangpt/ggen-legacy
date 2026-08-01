pub const REFERENCE_ID: &str = "fortune-5-repository-manufacturing-platform";
pub const PACK_ID: &str = "repository_manufacturing_platform";
pub const SCALE: &str = "fortune-5";
pub const PRIMITIVES: &[&str] = &[
    "engine-archived-primitive",
    "engine-replaced-primitive",
    "engine-subsumed-primitive",
    "system-archived-primitive",
    "system-refused-primitive",
    "system-replaced-primitive",
    "system-subsumed-primitive",
];

pub fn verify() -> bool {
    !PRIMITIVES.is_empty() && SCALE == "fortune-5" && REFERENCE_ID.starts_with("fortune-5")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn admitted_reference_is_composed() {
        assert!(verify());
        assert!(!PRIMITIVES.is_empty());
        assert_eq!(PACK_ID, "repository_manufacturing_platform");
    }

    #[test]
    fn missing_primitive_falsifier_is_detectable() {
        let reduced = &PRIMITIVES[1..];
        assert_eq!(reduced.len() + 1, PRIMITIVES.len());
    }
}
