import { AuthResponse } from '@/types/user';
import { Todo, TodoCreateInput, TodoUpdateInput } from '@/types/todo';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://anooshaqasim-phase3-chatbit-backend.hf.space';

interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  details?: any;
}

class ApiClient {
  private baseUrl: string;
  public token: string | null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  }

  setToken(token: string | null) {
    this.token = token;
    if (typeof window !== 'undefined') {
      if (token) {
        localStorage.setItem('access_token', token);
      } else {
        localStorage.removeItem('access_token');
      }
    }
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;

    const headers = {
      'Content-Type': 'application/json',
      ...(this.token && { 'Authorization': `Bearer ${this.token}` }),
      ...options.headers,
    };

    try {
      console.log(`[API] ${options.method || 'GET'} ${url}`, {
        token: this.token ? this.token.substring(0, 20) + '...' : 'No token',
        headers
      });

      const response = await fetch(url, {
        ...options,
        headers,
      });

      const data = await response.json();

      console.log(`[API] Response status: ${response.status}`, data);

      if (!response.ok) {
        // Extract error message from various response formats
        let errorMessage = `HTTP error! status: ${response.status}`;

        if (typeof data === 'object' && data !== null) {
          if (data.detail && typeof data.detail === 'string') {
            errorMessage = data.detail;
          } else if (data.message && typeof data.message === 'string') {
            errorMessage = data.message;
          } else if (data.error) {
            if (typeof data.error === 'string') {
              errorMessage = data.error;
            } else if (typeof data.error === 'object' && data.error.message) {
              errorMessage = data.error.message;
            } else {
              errorMessage = JSON.stringify(data.error);
            }
          }
        }

        console.error(`[API] Error: ${errorMessage}`, data);

        return {
          success: false,
          error: errorMessage,
          details: data
        };
      }

      // Transform response data from snake_case to camelCase
      let transformedData = data.data || data;

      // If transformedData is an array, transform each item
      if (Array.isArray(transformedData)) {
        transformedData = transformedData.map(item => transformFromSnakeToCamel(item));
      } else if (transformedData && typeof transformedData === 'object') {
        // If it's a single object, transform it recursively
        transformedData = transformFromSnakeToCamel(transformedData);

        // Special handling for nested tasks array (from getTasks endpoint)
        if (transformedData.tasks && Array.isArray(transformedData.tasks)) {
          transformedData.tasks = transformedData.tasks.map((item: any) => transformFromSnakeToCamel(item));
        }
      }

      return {
        success: true,
        data: transformedData,
        message: data.message
      };
    } catch (error: any) {
      console.error(`[API] Catch error: ${error.message}`, error);
      return {
        success: false,
        error: error.message || 'Network error occurred',
      };
    }
  }

  // Authentication methods
  async login(email: string, password: string): Promise<ApiResponse<AuthResponse['data']>> {
    return this.request<AuthResponse['data']>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async signup(email: string, password: string, name?: string): Promise<ApiResponse<AuthResponse['data']>> {
    return this.request<AuthResponse['data']>('/api/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ email, password, name }),
    });
  }

  // Task methods
  async getTasks(): Promise<ApiResponse<Todo[]>> {
    return this.request<Todo[]>('/api/tasks/');
  }

  async createTask(task: TodoCreateInput): Promise<ApiResponse<Todo>> {
    // Transform camelCase to snake_case for API request
    const snakeCaseTask = transformToSnakeCase(task);
    return this.request<Todo>('/api/tasks/', {
      method: 'POST',
      body: JSON.stringify(snakeCaseTask),
    });
  }

  async updateTask(userTaskId: number, task: TodoUpdateInput): Promise<ApiResponse<Todo>> {
    const snakeCaseTask = transformToSnakeCase(task);
    // Backend uses /api/tasks/edit with user_task_id query param
    const params = new URLSearchParams({ user_task_id: userTaskId.toString() });

    // Add update fields as query params
    if (snakeCaseTask.title) params.append('new_title', snakeCaseTask.title);
    if (snakeCaseTask.description !== undefined && snakeCaseTask.description !== null) params.append('description', snakeCaseTask.description);
    if (snakeCaseTask.priority) params.append('priority', snakeCaseTask.priority);
    if (snakeCaseTask.due_date) params.append('due_date', snakeCaseTask.due_date);
    if (snakeCaseTask.completed !== undefined) params.append('completed', String(snakeCaseTask.completed));

    return this.request<Todo>(`/api/tasks/edit?${params.toString()}`, {
      method: 'PUT',
    });
  }

  async deleteTask(userTaskId: number): Promise<ApiResponse<null>> {
    // Backend uses /api/tasks/delete with user_task_id query param
    return this.request<null>(`/api/tasks/delete?user_task_id=${userTaskId}`, {

      method: 'DELETE',
    });
  }

  async toggleTask(userTaskId: number): Promise<ApiResponse<Todo>> {
  return this.request<Todo>(`/api/tasks/toggle?user_task_id=${userTaskId}`, {
    method: 'PATCH',
  });
}



  // Chat methods
  async sendChatMessage(message: string, conversationId?: number): Promise<ApiResponse<{
    message: string;
    conversationId: number;
    toolResults?: any[];
  }>> {
    return this.request('/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        conversation_id: conversationId
      }),
    });
  }

  async getConversations(): Promise<ApiResponse<Array<{
    id: number;
    userId: string;
    createdAt: string;
    updatedAt: string;
  }>>> {
    return this.request('/api/conversations');
  }

  async getConversationMessages(conversationId: number): Promise<ApiResponse<Array<{
    id: number;
    conversationId: number;
    userId: string;
    role: string;
    content: string;
    createdAt: string;
  }>>> {
    return this.request(`/api/conversations/${conversationId}/messages`);
  }
}

// Helper function to convert snake_case keys to camelCase
function transformFromSnakeToCamel(obj: any): any {
  if (obj === null || typeof obj !== 'object' || Array.isArray(obj)) {
    return obj;
  }

  const convertedObj: any = {};
  for (const [key, value] of Object.entries(obj)) {
    // Convert snake_case to camelCase
    const camelCaseKey = key.replace(/_([a-z])/g, (match) => match[1].toUpperCase());
    // Recursively convert nested objects
    convertedObj[camelCaseKey] = typeof value === 'object' && value !== null && !Array.isArray(value)
      ? transformFromSnakeToCamel(value)
      : value;
  }
  return convertedObj;
}

// Helper function to convert camelCase keys to snake_case
function transformToSnakeCase(obj: any): any {
  if (obj === null || typeof obj !== 'object' || Array.isArray(obj)) {
    return obj;
  }

  const convertedObj: any = {};
  for (const [key, value] of Object.entries(obj)) {
    // Convert camelCase to snake_case
    const snakeCaseKey = key.replace(/[A-Z]/g, (match) => `_${match.toLowerCase()}`);
    // Recursively convert nested objects
    convertedObj[snakeCaseKey] = typeof value === 'object' && value !== null && !Array.isArray(value)
      ? transformToSnakeCase(value)
      : value;
  }
  return convertedObj;
}

export const apiClient = new ApiClient(API_BASE_URL);

export default ApiClient;