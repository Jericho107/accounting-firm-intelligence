# Controls matrix

| Risk | Preventive/detective control | Evidence |
|---|---|---|
| Duplicate operational keys | uniqueness validation before load | reverse tests |
| Orphan client facts | client foreign-key contract | validator + SQLite FK |
| Impossible invoice payment | paid amount constrained to [0, invoice amount] | unit test |
| Cross-grain double counting | aggregate facts before joins | mart test |
| Silent warehouse mutation | source-to-target counts and financial reconciliation | mutation test |
| AR ageing distortion | invoice-level ageing | ageing test |
| Capacity distortion | employee capacity joined only to employee time | capacity test |

The controls demonstrate design and deterministic synthetic evidence. They are not an audit opinion or regulatory certification.
