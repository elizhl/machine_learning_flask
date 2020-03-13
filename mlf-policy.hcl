path "/auth/token/lookup" {
	capabilities = ["read"]
}


path "/auth/token/lookup-self" {
	capabilities = ["read"]
}

path "/auth/token/roles/*" {
        capabilities = ["read"]
}

path "/auth/token/roles" {
        capabilities = ["list"]
}

path "identity/entity/id" {
        capabilities = ["list"]
}

path "/sys/auth" {
        capabilities = ["read"]
}

path "/sys/config/state/sanitized" {
        capabilities = ["read"]
}

path "/sys/host-info" {
        capabilities = ["read"]
}

path "/sys/metrics" {
        capabilities = ["read"]
}

path "/sys/mounts" {
        capabilities = ["read"]
}

path "/sys/policy" {
        capabilities = ["read"]
}

path "/sys/leases/lookup" {
        capabilities = ["create"]
}

path "/sys/leases/lookup/*" {
        capabilities = ["sudo", "list" ]
}

path "/sys/auth" {
        capabilities = ["read"]
}

path "/sys/token/accesors/*" {
        capabilities = ["sudo", "list" ]
}

