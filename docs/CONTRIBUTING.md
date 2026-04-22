# Branching Strategy

This project follows a lightweight GitHub Flow approach.

- `main` is the shared stable branch.
- Each issue is developed on a short-lived branch created from `main`.
- Work is merged into `main` through a pull request.
- Branches should be deleted after merge.
- Pull requests should reference the related GitHub issue.

Branch format:

```text
<type>/<issue-number>-<short-description>
```

Allowed types:

- `feature`: new functionality
- `bugfix`: bug fixes
- `docs`: documentation-only changes
- `chore`: setup, CI, dependencies, maintenance

Examples:

- `feature/7-repository-structure`
- `feature/8-eda-visualizations`
- `chore/9-ci-pipeline`
- `feature/5-fastapi-backend`
