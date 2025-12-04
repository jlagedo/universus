# ✅ **Complete, Reusable Code Review Prompt for Copilot**

**“I want you to perform a comprehensive, professional code review of my Python application. The project includes both a CLI interface and a NiceGUI-based desktop interface, and it uses a local SQLite database. Please analyze the code according to modern Python best practices, clean architecture principles, and standards for maintainability, readability, performance, and security.**

**For each file or module I provide, I want you to:**
- Identify issues, code smells, and anti‑patterns  
- Evaluate structure, naming, modularity, and separation of concerns  
- Check for security risks, especially around SQLite usage and user input  
- Review CLI and NiceGUI interface design patterns  
- Assess database interactions for correctness, efficiency, and safety  
- Highlight opportunities for refactoring or simplification  
- Recommend improvements with clear explanations  
- Provide actionable steps and example code snippets when appropriate  

**When you identify large or overly complex files, I want you to propose specific refactoring strategies. For each recommendation, provide:**
- A clear explanation of the problem  
- A suggested architectural or structural solution  
- Before/after code snippets demonstrating the improvement  
- Concrete examples of how the code could be reorganized  
- Optional alternative approaches when relevant  

**Examples of the types of solutions I want you to illustrate include:**
- Splitting large modules into smaller, domain‑focused modules  
- Extracting classes or functions from long files  
- Moving database logic into repositories or service layers  
- Separating UI, CLI, and business logic  
- Applying dependency injection or configuration patterns  
- Using dataclasses, pydantic models, or typed structures  
- Creating reusable components for NiceGUI  
- Abstracting SQLite operations into a dedicated data layer  

**At the end of the review, provide:**
- A summary of the overall health of the codebase  
- A prioritized action plan for improvements  

Let me know when you’re ready for the first file.”**
