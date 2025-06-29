// Main Application Logic
class ExpenseTracker {
  constructor() {
    this.expenses = [];
    this.categories = [];
    this.currentEditingExpense = null;
    this.currentEditingCategory = null;

    this.initializeApp();
  }

  async initializeApp() {
    this.bindEvents();
    await this.loadData();
    this.setCurrentDate();
  }

  // Event Bindings
  bindEvents() {
    // Tab switching
    document.querySelectorAll(".tab-button").forEach((button) => {
      button.addEventListener("click", (e) => {
        this.switchTab(e.target.dataset.tab);
      });
    });

    // Modal controls
    document.getElementById("addExpenseBtn").addEventListener("click", () => {
      this.openExpenseModal();
    });

    document.getElementById("addCategoryBtn").addEventListener("click", () => {
      this.openCategoryModal();
    });

    document
      .getElementById("closeExpenseModal")
      .addEventListener("click", () => {
        this.closeExpenseModal();
      });

    document
      .getElementById("closeCategoryModal")
      .addEventListener("click", () => {
        this.closeCategoryModal();
      });

    document.getElementById("cancelExpense").addEventListener("click", () => {
      this.closeExpenseModal();
    });

    document.getElementById("cancelCategory").addEventListener("click", () => {
      this.closeCategoryModal();
    });
    document.getElementById("analyticsBtn").addEventListener("click", () => {
      this.openAnalyticsModal();
      const expenseData =this.expenses
      
      
        

    // Group and sum by category
    const categoryTotals = {};
    expenseData.forEach(item => {
      if (categoryTotals[item.category.name]) {
        categoryTotals[item.category.name] += item.amount;
      } else {
        categoryTotals[item.category.name] = item.amount;
      }
    });

    const categories = Object.keys(categoryTotals);
    const amounts = Object.values(categoryTotals);

    const ctx = document.getElementById('myChart').getContext('2d');
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: categories,
        datasets: [{
          label: 'Amount Spent (₹)',
          data: amounts,
          backgroundColor: '#4CAF50',
          borderColor: '#388E3C',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Amount (₹)'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Expense Category'
            }
          }
        },
        plugins: {
          title: {
            display: true,
            text: 'Expenses by Category - Bar Chart'
          }
        }
      }
    });
    });
     
    document
      .getElementById("closeAnalyticsModal")
      .addEventListener("click", () => {
        this.closeAnalyticsModal();
      });

    // Form submissions
    document.getElementById("expenseForm").addEventListener("submit", (e) => {
      this.handleExpenseSubmit(e);
    });

    document.getElementById("categoryForm").addEventListener("submit", (e) => {
      this.handleCategorySubmit(e);
    });

    // Close modals on outside click
    window.addEventListener("click", (e) => {
      if (e.target.classList.contains("modal")) {
        e.target.style.display = "none";
      }
    });
  }

  // Tab Management
  switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll(".tab-button").forEach((button) => {
      button.classList.remove("active");
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add("active");

    // Update tab content
    document.querySelectorAll(".tab-content").forEach((content) => {
      content.classList.remove("active");
    });
    document.getElementById(tabName).classList.add("active");
  }

  // Data Loading
  async loadData() {
    // Load categories first, then expenses (so we can map category names to objects)
    await this.loadCategories();
    await this.loadExpenses();
    this.updateDashboard();
  }

  async loadExpenses() {
    try {
      this.showLoading("expensesLoading");
      const expenses = await expenseAPI.getAll();

      // Map category names to category objects for display
      this.expenses = expenses.map((expense) => {
        const categoryObj = this.categories.find(
          (c) => c.name === expense.category
        );
        return {
          ...expense,
          categoryId: categoryObj ? categoryObj.id : null,
          category: categoryObj || null,
        };
      });

      this.renderExpenses();
    } catch (error) {
      this.showToast("Failed to load expenses", "error");
    } finally {
      this.hideLoading("expensesLoading");
    }
  }

  async loadCategories() {
    try {
      this.showLoading("categoriesLoading");
      this.categories = await categoryAPI.getAll();
      this.renderCategories();
      this.populateCategorySelect();
    } catch (error) {
      this.showToast("Failed to load categories", "error");
    } finally {
      this.hideLoading("categoriesLoading");
    }
  }

  // Expense Management
  renderExpenses() {
    const container = document.getElementById("expensesList");
    const tableContainer = document.getElementById("expensesTableContainer");
    const emptyState = document.getElementById("expensesEmpty");

    if (this.expenses.length === 0) {
      container.innerHTML = "";
      tableContainer.style.display = "none";
      emptyState.style.display = "block";
      return;
    }

    emptyState.style.display = "none";
    tableContainer.style.display = "block";

    container.innerHTML = this.expenses
      .map(
        (expense) => `
            <tr>
                <td>
                    <div style="font-weight: 600; color: #333;">${
                      expense.description
                    }</div>
                </td>
                <td>
                    <span class="category-badge">
                        ${expense.category?.name || "Uncategorized"}
                    </span>
                </td>
                <td class="amount-cell">₹${expense.amount.toFixed(2)}</td>
                <td class="date-cell">${this.formatDate(expense.date)}</td>
                <td>
                    <div class="actions-cell">
                        <button class="btn btn-edit btn-sm" onclick="app.editExpense(${
                          expense.id
                        })">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button class="btn btn-danger btn-sm" onclick="app.deleteExpense(${
                          expense.id
                        })">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </td>
            </tr>
        `
      )
      .join("");
  }

  async editExpense(id) {
    const expense = this.expenses.find((e) => e.id === id);
    if (!expense) return;

    this.currentEditingExpense = expense;

    // Populate form
    document.getElementById("expenseAmount").value = expense.amount;
    document.getElementById("expenseDescription").value = expense.description;
    document.getElementById("expenseCategory").value = expense.categoryId || "";
    document.getElementById("expenseDate").value = expense.date;

    // Update modal title and button
    document.getElementById("expenseModalTitle").textContent = "Edit Expense";
    document.getElementById("expenseSubmitText").textContent = "Update Expense";

    this.openExpenseModal();
  }

  async deleteExpense(id) {
    if (!confirm("Are you sure you want to delete this expense?")) return;

    try {
      await expenseAPI.delete(id);
      this.expenses = this.expenses.filter((e) => e.id !== id);
      this.renderExpenses();
      this.updateDashboard();
      this.showToast("Expense deleted successfully");
    } catch (error) {
      this.showToast("Failed to delete expense", "error");
    }
  }

  // Category Management
  renderCategories() {
    const container = document.getElementById("categoriesList");
    const tableContainer = document.getElementById("categoriesTableContainer");
    const emptyState = document.getElementById("categoriesEmpty");

    if (this.categories.length === 0) {
      container.innerHTML = "";
      tableContainer.style.display = "none";
      emptyState.style.display = "block";
      return;
    }

    emptyState.style.display = "none";
    tableContainer.style.display = "block";

    container.innerHTML = this.categories
      .map(
        (category) => `
            <tr>
                <td>
                    <div style="font-weight: 600; color: #333;">${
                      category.name
                    }</div>
                </td>
               
               
                <td>
                    <div class="actions-cell">
                        <button class="btn btn-edit btn-sm" onclick="app.editCategory(${
                          category.id
                        })">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button class="btn btn-danger btn-sm" onclick="app.deleteCategory(${
                          category.id
                        })">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </td>
            </tr>
        `
      )
      .join("");
  }

  async editCategory(id) {
    const category = this.categories.find((c) => c.id === id);
    if (!category) return;

    this.currentEditingCategory = category;

    // Populate form
    document.getElementById("categoryName").value = category.name;

    // Update modal title and button
    document.getElementById("categoryModalTitle").textContent = "Edit Category";
    document.getElementById("categorySubmitText").textContent =
      "Update Category";

    this.openCategoryModal();
  }

  async deleteCategory(id) {
    // Check if category has expenses
    const hasExpenses = this.expenses.some((e) => e.categoryId === id);

    if (hasExpenses) {
      if (
        !confirm(
          "This category has expenses. Deleting it will remove the category from those expenses. Continue?"
        )
      ) {
        return;
      }
    } else {
      if (!confirm("Are you sure you want to delete this category?")) {
        return;
      }
    }

    try {
      await categoryAPI.delete(id);
      this.categories = this.categories.filter((c) => c.id !== id);

      // Update expenses that used this category
      this.expenses = this.expenses.map((expense) => {
        if (expense.categoryId === id) {
          return { ...expense, categoryId: null, category: null };
        }
        return expense;
      });

      this.renderCategories();
      this.renderExpenses();
      this.populateCategorySelect();
      this.updateDashboard();
      this.showToast("Category deleted successfully");
    } catch (error) {
      this.showToast("Failed to delete category", "error");
    }
  }

  // Modal Management
  openExpenseModal() {
    document.getElementById("expenseModal").style.display = "block";
  }
  openAnalyticsModal() {
    document.getElementById("analytics").style.display = "block";
  }

  closeExpenseModal() {
    document.getElementById("expenseModal").style.display = "none";
    document.getElementById("expenseForm").reset();
    document.getElementById("expenseModalTitle").textContent = "Add Expense";
    document.getElementById("expenseSubmitText").textContent = "Add Expense";
    this.currentEditingExpense = null;
  }

  openCategoryModal() {
    document.getElementById("categoryModal").style.display = "block";
  }

  closeCategoryModal() {
    document.getElementById("categoryModal").style.display = "none";
    document.getElementById("categoryForm").reset();
    document.getElementById("categoryModalTitle").textContent = "Add Category";
    document.getElementById("categorySubmitText").textContent = "Add Category";
    this.currentEditingCategory = null;
  }

  closeAnalyticsModal() {
    document.getElementById("analytics").style.display = "none";
  }

  // Form Handlers
  async handleExpenseSubmit(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const categoryId = parseInt(
      formData.get("category") ||
        document.getElementById("expenseCategory").value
    );

    // Find the category to get its name
    const category = this.categories.find((c) => c.id === categoryId);

    const expenseData = {
      amount: parseFloat(
        formData.get("amount") || document.getElementById("expenseAmount").value
      ),
      description:
        formData.get("description") ||
        document.getElementById("expenseDescription").value,
      category: category ? category.name : "Uncategorized", // Send category name instead of categoryId
      date:
        formData.get("date") || document.getElementById("expenseDate").value,
    };

    try {
      if (this.currentEditingExpense) {
        // Update existing expense
        const updatedExpense = await expenseAPI.update(
          this.currentEditingExpense.id,
          expenseData
        );
        const index = this.expenses.findIndex(
          (e) => e.id === this.currentEditingExpense.id
        );
        // Add category info for display
        this.expenses[index] = { ...updatedExpense, categoryId, category };
        this.showToast("Expense updated successfully");
      } else {
        // Create new expense
        const newExpense = await expenseAPI.create(expenseData);
        // Add category info for display
        this.expenses.push({ ...newExpense, categoryId, category });
        this.showToast("Expense added successfully");
      }

      this.renderExpenses();
      this.updateDashboard();
      this.closeExpenseModal();
    } catch (error) {
      this.showToast("Failed to save expense", "error");
    }
  }

  async handleCategorySubmit(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const categoryData = {
      name:
        formData.get("name") || document.getElementById("categoryName").value,
    };

    try {
      if (this.currentEditingCategory) {
        // Update existing category
        const updatedCategory = await categoryAPI.update(
          this.currentEditingCategory.id,
          categoryData
        );
        const index = this.categories.findIndex(
          (c) => c.id === this.currentEditingCategory.id
        );
        this.categories[index] = updatedCategory;

        // Update expenses with this category
        this.expenses = this.expenses.map((expense) => {
          if (expense.categoryId === this.currentEditingCategory.id) {
            return { ...expense, category: updatedCategory };
          }
          return expense;
        });

        this.showToast("Category updated successfully");
      } else {
        // Create new category
        const newCategory = await categoryAPI.create(categoryData);
        this.categories.push(newCategory);
        this.showToast("Category added successfully");
      }

      this.renderCategories();
      this.renderExpenses();
      this.populateCategorySelect();
      this.updateDashboard();
      this.closeCategoryModal();
    } catch (error) {
      this.showToast("Failed to save category", "error");
    }
  }

  // Utility Methods
  populateCategorySelect() {
    const select = document.getElementById("expenseCategory");
    select.innerHTML =
      '<option value="">Select a category</option>' +
      this.categories
        .map(
          (category) =>
            `<option value="${category.id}">${category.name}</option>`
        )
        .join("");
  }

  updateDashboard() {
    const totalExpenses = this.expenses.reduce(
      (sum, expense) => sum + expense.amount,
      0
    );
    const currentMonth = new Date().getMonth();
    const currentYear = new Date().getFullYear();

    const monthlyExpenses = this.expenses
      .filter((expense) => {
        const expenseDate = new Date(expense.date);
        return (
          expenseDate.getMonth() === currentMonth &&
          expenseDate.getFullYear() === currentYear
        );
      })
      .reduce((sum, expense) => sum + expense.amount, 0);

    document.getElementById(
      "totalExpenses"
    ).textContent = `₹${totalExpenses.toFixed(2)}`;
    document.getElementById(
      "monthlyExpenses"
    ).textContent = `₹${monthlyExpenses.toFixed(2)}`;
    document.getElementById("categoriesCount").textContent =
      this.categories.length;
  }

  getCategoryExpenseCount(categoryId) {
    return this.expenses.filter((e) => e.categoryId === categoryId).length;
  }

  getCategoryTotal(categoryId) {
    return this.expenses
      .filter((e) => e.categoryId === categoryId)
      .reduce((sum, e) => sum + e.amount, 0);
  }

  formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  }

  setCurrentDate() {
    const today = new Date().toISOString().split("T")[0];
    document.getElementById("expenseDate").value = today;
  }

  showLoading(elementId) {
    document.getElementById(elementId).style.display = "block";
  }

  hideLoading(elementId) {
    document.getElementById(elementId).style.display = "none";
  }

  showToast(message, type = "success") {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;

    const icon =
      type === "error"
        ? "fas fa-exclamation-circle"
        : type === "warning"
        ? "fas fa-exclamation-triangle"
        : "fas fa-check-circle";

    toast.innerHTML = `
            <i class="${icon}"></i>
            <span>${message}</span>
        `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.remove();
    }, 3000);
  }
}

// Initialize the application when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  window.app = new ExpenseTracker();
});
