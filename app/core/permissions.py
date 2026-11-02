
# Permission format: resource:action

DEFAULT_PERMISSIONS = [
    # Account permissions
    ("account:read", "View financial accounts"),
    ("account:create", "Create financial accounts"),
    ("account:update", "Update financial accounts"),
    ("account:delete", "Delete financial accounts"),

    # Category permissions
    ("category:read", "View transaction categories"),
    ("category:create", "Create transaction categories"),
    ("category:update", "Update transaction categories"),
    ("category:delete", "Delete transaction categories"),

    # Transaction permissions
    ("transaction:read", "View transactions"),
    ("transaction:create", "Create transactions"),
    ("transaction:update", "Update transactions"),
    ("transaction:delete", "Delete transactions"),

    # Budget permissions
    ("budget:read", "View budgets"),
    ("budget:create", "Create budgets"),
    ("budget:update", "Update budgets"),
    ("budget:delete", "Delete budgets"),

    # Report permissions
    ("report:read", "View financial reports"),

    # User management permissions
    ("user:read", "View users"),
    ("user:update", "Update users"),
    ("user:delete", "Delete users"),

    # Role and permission management
    ("role:read", "View roles"),
    ("role:manage", "Manage roles and permissions"),
]


# Permissions assigned to normal users.
USER_PERMISSIONS = {
    "account:read",
    "account:create",
    "account:update",
    "account:delete",

    "category:read",
    "category:create",
    "category:update",
    "category:delete",

    "transaction:read",
    "transaction:create",
    "transaction:update",
    "transaction:delete",

    "budget:read",
    "budget:create",
    "budget:update",
    "budget:delete",

    "report:read",
}


# Permissions assigned to administrators.
ADMIN_PERMISSIONS = {
    code for code, description in DEFAULT_PERMISSIONS
}
