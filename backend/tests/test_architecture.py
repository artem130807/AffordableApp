import ast
from pathlib import Path


def test_dependencies_point_toward_domain() -> None:
    source_root = Path("src/app")

    for path in (source_root / "domain").rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "app.application" not in source, path
        assert "app.infrastructure" not in source, path
        assert "app.presentation" not in source, path

    for path in (source_root / "application").rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "app.infrastructure" not in source, path
        assert "app.presentation" not in source, path


def test_cqrs_modules_have_one_handler_per_use_case() -> None:
    cqrs_root = Path("src/app/application/cqrs")
    assert not [path for path in cqrs_root.glob("*.py") if path.name != "__init__.py"]

    for path in cqrs_root.rglob("*.py"):
        if path.name == "__init__.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        handlers = [
            node.name
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name.endswith("Handler")
        ]
        expected_count = 0 if path.name == "token_pair.py" else 1
        assert len(handlers) == expected_count, (
            f"{path} must contain {expected_count} handler, found: {handlers}"
        )


def test_each_repository_has_its_own_module() -> None:
    assert not Path("src/app/domain/repositories.py").exists()
    assert not Path("src/app/infrastructure/repositories.py").exists()
    for relative_root in (
        "src/app/domain/repositories",
        "src/app/infrastructure/repositories",
    ):
        repository_root = Path(relative_root)
        for path in repository_root.glob("*_repository.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            repositories = [
                node.name
                for node in tree.body
                if isinstance(node, ast.ClassDef) and node.name.endswith("Repository")
            ]
            assert len(repositories) == 1, f"{path} must contain one repository"


def test_routes_use_unit_of_work_instead_of_constructing_repositories() -> None:
    routes_root = Path("src/app/presentation/api/routes")
    for path in routes_root.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "app.infrastructure.repositories" not in source, path


def test_routes_do_not_wire_infrastructure_adapters() -> None:
    routes_root = Path("src/app/presentation/api/routes")
    for path in routes_root.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "app.infrastructure" not in source, path
