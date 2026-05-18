def audit_pack(pack):
    return {"entry_count": len(pack.entries), "active_count": sum(1 for e in pack.entries if e.active)}
