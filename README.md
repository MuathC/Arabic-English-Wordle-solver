# AI Wordle Solver

This project implements four AI-driven approaches to solve Wordle puzzles efficiently. The strategies include:

- **Constraint Satisfaction Problem (CSP)**
- **Letter Frequency Analysis**
- **Bayesian Updating**
- **Entropy Maximization**

The goal is to determine the most effective method for solving Wordle with minimal attempts while ensuring computational efficiency.

---

## Performance Insights 🏆

### **Entropy Maximization Agent**
- **Win Rate**: 100%
- **Average Guesses per Win**: 3.92 
- **Average Time per Game**: 6.47s

### **Frequency Heuristic Agent**
- **Win Rate**: 95.63%
- **Average Guesses per Win**: 4.04
- **Average Time per Game**: 0.04s

### **CSP Agent**
- **Win Rate**: 94.99%
- **Average Guesses per Win**: 4.40
- **Average Time per Game**: *0.03s*

### **Bayesian Agent**
- **Win Rate**: 94.81%
- **Average Guesses per Win**: 4.40
- **Average Time per Game**: 0.52s 

## Prerequisites 🧰

Before running the project for the first time, make sure you have the required dependencies installed, and pre-computed data generated:

1. **Create a virtual environment** 🛠️:

    - On **Windows**:
        ```powershell
        py -m venv .venv
        ```

    - On **macOS/Linux**:
        ```bash
        python3 -m venv .venv
        ```

    This command creates a `.venv` directory that holds a self-contained Python environment.


2. **Activate the virtual environment** 🔑:

    Before you start using the app, you'll need to `activate` the virtual environment:
    
    - On **Windows**:
    ```powershell
    .venv\Scripts\activate
    ```
    - On **macOS/Linux**:
    ```bash
    source .venv/bin/activate
    ```

    > **Note 📝**: Closing your shell will deactivate the virtual environment. If you want to use the app again, `reactivate` the virtual environment by following the same activation procedure. There's no need to create a new virtual environment.
    
    **If you want to switch projects or leave your virtual environment, `deactivate` the environment:**
    ```bash
    deactivate
    ```
3. **Install dependencies** 📦:

    After creating and activating the virtual environment, you need to install the required dependencies for the project. *This step only needs to be done once.*
    ```bash
    pip install -r requirements.txt
    ```

4. **Pre-compute cache data for entropy agent to avoid potential crashes** ⚙️:  
    >*This process may take a while.*
    ```bash
    python data/pre_compute.py
    ```
    **Note 📝**: This step is only required once, or if the `entropy_cache.json` file is missing or deleted from the `data` directory.

5. **Run the main application** 🚀

   To run the app:

    ```bash
    python main/app.py
    ```

For a detailed analysis of the agents and their performance, refer to the [Project Report](./reports/Project_Report.pdf) in the `reports` directory.
