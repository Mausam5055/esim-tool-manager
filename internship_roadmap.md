# eSim Tool Manager - 2-Month Internship Roadmap

## 🎯 Project Overview
This document outlines the project requirements and an 8-week roadmap for the eSim Summer Fellowship (Internship). The goal is to further develop, improve, and test the **eSim Automated Tool Manager**, culminating in a seamless integration with **eSim 2.6**.

## 📌 Core Objectives
1. **Enhance Existing Features**: Improve the GUI/CLI, refine the Docker generation system, and fix known issues (e.g., Windows Ngspice installation fallback).
2. **eSim 2.6 Integration**: Ensure the tool manager acts as the native dependency resolution and installation engine for the upcoming eSim 2.6 release.
3. **Advanced Features Development**: Implement a plugin system, telemetry/analytics, and a background auto-update mechanism.
4. **Testing & QA**: Rigorously test the application across Windows, macOS, and Linux, ensuring stable Docker container generation.

---

## 🗓️ Weekly Roadmap (8 Weeks)

### Phase 1: Foundation & Polish (Weeks 1-2)
**Week 1: Codebase Review & Bug Squashing**
- [ ] Review current architecture (`cli.py`, `gui.py`, `installer.py`, `updater.py`).
- [ ] Fix the Windows `ngspice` fallback URL issue (replace the source code archive with a compiled `.exe` direct link in `data/tools_registry.json`).
- [ ] Improve error handling and logging granularity across all modules.

**Week 2: UI/UX Improvements**
- [ ] Refine the CustomTkinter GUI layout for better accessibility, responsiveness, and aesthetics.
- [ ] Enhance CLI rich outputs (add better progress bars during downloads/extractions).
- [ ] Finalize the Dockerfile generation (`docker_generator.py`) to support multi-stage builds if necessary.

### Phase 2: Feature Expansion (Weeks 3-4)
**Week 3: Auto-Update & Telemetry**
- [ ] Implement a background checking mechanism for tool updates (`updater.py`).
- [ ] Add basic anonymous telemetry (e.g., successful installs, OS version) to help the eSim team track usage and errors (opt-in via `config.py`).
- [ ] Create tests for these new mechanisms.

**Week 4: Plugin System for Tool Definitions**
- [ ] Develop a community plugin system where users can drop custom `[tool].json` definitions into a specific folder to add non-standard tools.
- [ ] Ensure the dependency checker can parse and validate these custom definitions.
- [ ] Write unit tests for the new plugin architecture.

### Phase 3: eSim 2.6 Integration (Weeks 5-6)
**Week 5: Integration Architecture & API**
- [ ] Coordinate with the eSim 2.6 core team to understand how they currently invoke external tools.
- [ ] Create a Python API wrapper in `tool_manager/` so eSim 2.6 can programmatically call the Tool Manager without using the CLI or GUI.
- [ ] Map eSim 2.6 environment variables to the Tool Manager's configuration.

**Week 6: Deep Integration & Workflow Testing**
- [ ] Implement hooks in eSim 2.6 that trigger the Tool Manager upon startup to verify if Ngspice, KiCad, or OpenModelica are missing.
- [ ] Build a seamless "Install Missing Tools" prompt directly into the eSim 2.6 interface.
- [ ] Ensure `env_manager.py` correctly passes PATH variables back to the active eSim session.

### Phase 4: Validation & Handover (Weeks 7-8)
**Week 7: Cross-Platform Testing & QA**
- [ ] Run extensive end-to-end (E2E) tests on Windows 10/11, Ubuntu, and macOS.
- [ ] Test Edge Cases: Network drops during installation, permission denials, and corrupt package managers (apt/brew/choco).
- [ ] Verify the Docker environment cleanly builds and runs EDA tools.

**Week 8: Documentation & Final Delivery**
- [ ] Update `README.md` with new features, architecture diagrams, and API docs.
- [ ] Write user documentation for the eSim 2.6 manual regarding the new Tool Manager.
- [ ] Code cleanup (PEP8 compliance check) and final pull request submission.
- [ ] Prepare the Final Internship Report/Presentation.

---

## 📦 Key Deliverables
1. **Stable Tool Manager Release**: Fully working cross-platform tool manager without installation hiccups.
2. **eSim 2.6 PR**: A merged Pull Request into the main eSim repository integrating the tool manager.
3. **Plugin Architecture**: A working directory for custom tool JSON configurations.
4. **Documentation**: Updated README, Wiki, and eSim user manual pages.

> **Note:** This is a living document. Timelines and priorities may adjust based on feedback from the eSim core team during the internship.
