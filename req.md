# Environment Management System - Requirements

## 1. User Management

- **One Admin only** - system has exactly one admin user
- **Admin creates users** - admin can create Team Lead, Developer, DevOps, QA users
- **No self-registration** - users cannot register themselves
- **Five roles**: `ADMIN`, `TEAM_LEAD`, `DEVELOPER`, `DEVOPS`, `QA`
- **Admin has full access** - admin can do everything

---

## 2. Database Models

- **USER** - id, email, name, role, is_active
- **INTEGRATION** - id, name, description, owner, created_at
- **USER_INTEGRATION** - user_id, integration_id
- **ENVIRONMENT** - id, integration_id, environment_type (Dev, QA, UAT, Production), title, content, note, updated_by, updated_at, created_at

---

## 3. Relationships

- **USER** → has many → **INTEGRATIONS**
- **INTEGRATION** → has many → **USERS**
  - (USER many-to-many INTEGRATION)
- **INTEGRATION** → has many → **ENVIRONMENTS**

---

## 4. Permissions

### Admin
- Can do everything
- Can create users (Team Lead, Developer, DevOps, QA)

### Team Lead
- Can create integrations
- Can assign developers to integrations
- Can remove users from integrations
- Can remove integrations

### Developer (Assigned)
- Can create environments for assigned integration
- Can edit environments for assigned integration
- Can view environment details

### Developer (Not Assigned)
- Can only view environment details
- Must request Team Lead to be assigned to integration for edit access

### DevOps & QA
- Can only view environment details

---

## 5. Workflow

1. Admin creates Team Lead, Developers, DevOps, QA users
2. Team Lead creates integrations
3. Team Lead assigns developers to integrations
4. Assigned developers can create and edit environments
5. Other users (developers, devops, qa) can only view environments
6. If a developer needs edit access to another integration:
   - Developer requests permission from Team Lead
   - Team Lead assigns developer to that integration
   - Developer can now create/edit environments
7. Team Lead can remove users from integrations
8. Team Lead can remove integrations

---