// API Service Layer
class ApiService {
  constructor() {
    this.baseURL = "http://localhost:5000/api";
    this.timeout = 10000;
    this.headers = {
      "Content-Type": "application/json",
      Accept: "application/json",
    };
  }

  // Generic HTTP request method
  async request(url, options = {}) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(`${this.baseURL}${url}`, {
        headers: { ...this.headers, ...options.headers },
        signal: controller.signal,
        ...options,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      if (error.name === "AbortError") {
        throw new Error("Request timeout");
      }
      throw error;
    }
  }

  // GET request
  async get(url) {
    return this.request(url, { method: "GET" });
  }

  // POST request
  async post(url, data) {
    return this.request(url, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // PUT request
  async put(url, data) {
    return this.request(url, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  // DELETE request
  async delete(url) {
    return this.request(url, { method: "DELETE" });
  }
}

// Expense API methods
class ExpenseAPI {
  constructor() {
    this.api = new ApiService();
    this.endpoint = "/expenses";
  }

  // Get all expenses
  async getAll() {
    return await this.api.get(this.endpoint);
  }

  // Get expense by ID
  async getById(id) {
    return await this.api.get(`${this.endpoint}/${id}`);
  }

  // Create new expense
  async create(expenseData) {
    return await this.api.post(this.endpoint, expenseData);
  }

  // Update expense
  async update(id, expenseData) {
    return await this.api.put(`${this.endpoint}/${id}`, expenseData);
  }

  // Delete expense
  async delete(id) {
    return await this.api.delete(`${this.endpoint}/${id}`);
  }
}

// Category API methods
class CategoryAPI {
  constructor() {
    this.api = new ApiService();
    this.endpoint = "/categories";
  }

  // Get all categories
  async getAll() {
    return await this.api.get(this.endpoint);
  }

  // Get category by ID
  async getById(id) {
    return await this.api.get(`${this.endpoint}/${id}`);
  }

  // Create new category
  async create(categoryData) {
    return await this.api.post(this.endpoint, categoryData);
  }

  // Update category
  async update(id, categoryData) {
    return await this.api.put(`${this.endpoint}/${id}`, categoryData);
  }

  // Delete category
  async delete(id) {
    return await this.api.delete(`${this.endpoint}/${id}`);
  }
}

// Initialize API instances
const expenseAPI = new ExpenseAPI();
const categoryAPI = new CategoryAPI();

// Export for use in other files
window.expenseAPI = expenseAPI;
window.categoryAPI = categoryAPI;
