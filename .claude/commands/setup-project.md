# Setup New Project

Initialize new project with best-practice templates, configs, and CI/CD.

## What This Does

CTO coordinates project setup with all necessary boilerplate, configs, and infrastructure.

## Usage

```
/setup-project [project name] [tech stack] [project type]
```

## Example

```
/setup-project "ai-analytics-api" "Python FastAPI, PostgreSQL, Redis" "backend-api"
/setup-project "react-dashboard" "React, TypeScript, Tailwind" "frontend"
/setup-project "microservice" "Node.js, Express, MongoDB" "microservice"
```

## Process

1. **Project Structure** (cto + system-architect)
   - Directory structure based on best practices
   - Module organization
   - Configuration management
   - Environment separation (dev, staging, prod)

2. **Frontend Setup** (frontend-developer, if applicable)
   - React/Next.js project initialization
   - TypeScript configuration
   - ESLint + Prettier setup
   - Tailwind CSS / styled-components
   - Component library setup
   - State management (Redux, Zustand, etc.)
   - Routing configuration

3. **Backend Setup** (backend-architect, if applicable)
   - Framework initialization (FastAPI, Express, Django)
   - Project structure (MVC, Clean Architecture)
   - Database connection setup
   - ORM configuration (SQLAlchemy, Prisma, Mongoose)
   - Authentication boilerplate
   - API versioning
   - Error handling middleware
   - Logging setup

4. **Database Setup** (database-architect)
   - Database schema design
   - Migration framework setup (Alembic, Knex, Prisma)
   - Seed data scripts
   - Database indexes
   - Connection pooling

5. **DevOps Configuration** (devops-engineer)
   - Dockerfile (multi-stage builds)
   - docker-compose.yml (local development)
   - Kubernetes manifests (if applicable)
   - Terraform infrastructure code
   - Environment variable templates (.env.example)
   - Health check endpoints

6. **CI/CD Pipeline** (devops-engineer)
   - GitHub Actions workflows
   - Automated testing
   - Code quality checks (ESLint, Black, Flake8)
   - Security scanning
   - Build and push Docker images
   - Automated deployment (staging)
   - Branch protection rules

7. **Testing Setup** (test-engineer)
   - Test framework configuration (Jest, Pytest, Vitest)
   - Test directory structure
   - Sample unit tests
   - Integration test examples
   - E2E test setup (Playwright, Cypress)
   - Coverage reporting
   - Test CI integration

8. **Code Quality** (code-reviewer)
   - Linting configuration
   - Code formatter setup
   - Pre-commit hooks (Husky, pre-commit)
   - Git commit message standards
   - Branch naming conventions
   - Code review checklist

9. **Security Setup** (security-auditor)
   - Dependency scanning (Dependabot, Snyk)
   - Secret management setup
   - CORS configuration
   - Rate limiting
   - Security headers
   - .gitignore (with secrets protection)

10. **Documentation** (technical-writer)
    - README.md with setup instructions
    - CONTRIBUTING.md
    - CODE_OF_CONDUCT.md (if open source)
    - LICENSE file
    - API documentation setup
    - Architecture overview

11. **Monitoring Setup** (devops-engineer)
    - Logging configuration
    - Metrics collection
    - Error tracking (Sentry setup)
    - Performance monitoring
    - Healthcheck endpoints

## Deliverables

- Complete project structure
- All configuration files
- Dockerfile and docker-compose.yml
- CI/CD pipeline (GitHub Actions)
- Testing framework setup
- Documentation (README, CONTRIBUTING)
- Pre-commit hooks
- Environment templates
- Sample code and tests
- Database migrations
- Infrastructure as Code (Terraform)

## Tech Stack Templates

**Python FastAPI:**
- FastAPI + SQLAlchemy + PostgreSQL
- Alembic migrations
- Pytest + coverage
- Black + isort + flake8
- Docker + docker-compose

**Node.js Express:**
- Express + TypeScript
- Prisma ORM + PostgreSQL
- Jest + supertest
- ESLint + Prettier
- Docker + docker-compose

**React Frontend:**
- React + TypeScript + Vite
- Tailwind CSS
- React Router
- Zustand/Redux
- Vitest + React Testing Library

**Next.js Full-Stack:**
- Next.js 14+ (App Router)
- TypeScript
- Prisma + PostgreSQL
- Tailwind CSS
- NextAuth.js

## Time Estimate

- Frontend project: 1-2 hours
- Backend API: 2-3 hours
- Full-stack project: 3-5 hours
- Microservice with infrastructure: 4-6 hours

## Post-Setup Checklist

- [ ] All dependencies install successfully
- [ ] Tests run and pass
- [ ] Docker build succeeds
- [ ] Local development environment works
- [ ] CI/CD pipeline runs successfully
- [ ] Documentation is clear
- [ ] Security best practices implemented
- [ ] Code quality checks pass
