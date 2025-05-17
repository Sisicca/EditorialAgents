import axios from 'axios';

// API基础URL
const API_BASE_URL = 'http://127.0.0.1:8000';

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 添加请求拦截器进行调试
apiClient.interceptors.request.use(
  config => {
    console.log('API请求:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      data: config.data,
      headers: config.headers
    });
    return config;
  },
  error => {
    console.error('API请求错误:', error);
    return Promise.reject(error);
  }
);

// 添加响应拦截器进行调试
apiClient.interceptors.response.use(
  response => {
    console.log('API响应:', {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
      data: response.data
    });
    return response;
  },
  error => {
    console.error('API响应错误:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data || error.message,
      config: error.config
    });
    return Promise.reject(error);
  }
);

// 定义API接口类型
export interface CreateProcessInput {
  topic: string;
  description?: string;
  problem?: string;
}

export interface OutlineNode {
  id: string;
  title: string;
  summary?: string;
  level: number;
  children?: OutlineNode[];
}

export interface ProcessCreationResponse {
  process_id: string;
  topic: string;
  initial_outline: OutlineNode;
  message: string;
}

export interface OutlineUpdateRequest {
  outline_dict: OutlineNode;
}

export interface OutlineUpdateResponse {
  process_id: string;
  message: string;
}

export interface RetrievalStartRequest {
  use_web: boolean;
  use_kb: boolean;
}

export interface DocumentPreview {
  id: string;
  citation_key: string;
  title?: string;
  source: string;
}

export interface LeafNodeStatus {
  node_id: string;
  title: string;
  status_message: string;
  current_query?: string;
  iteration_progress?: string;
  retrieved_docs_preview: DocumentPreview[];
  content_preview?: string;
  is_completed: boolean;
  error_message?: string;
  last_updated: string;
}

export interface RetrievalOverallStatus {
  overall_status_message: string;
  total_leaf_nodes: number;
  completed_leaf_nodes: number;
  leaf_nodes_status: Record<string, LeafNodeStatus>;
  start_time?: string;
  end_time?: string;
  error_message?: string;
}

export interface RetrievalStartResponse {
  process_id: string;
  message: string;
  initial_status: RetrievalOverallStatus;
}

export interface RetrievalStatusResponse {
  process_id: string;
  retrieval_status: RetrievalOverallStatus;
}

export interface CompositionStartResponse {
  process_id: string;
  message: string;
}

export interface ArticleResponse {
  process_id: string;
  composition_status: string;
  article_content?: string;
  references_raw?: any[];
}

// API服务
const apiService = {
  // 测试API连接
  testConnection: async (): Promise<any> => {
    try {
      const response = await apiClient.get('/health');
      return response.data;
    } catch (error) {
      console.error('API连接测试失败:', error);
      throw error;
    }
  },

  // 创建新流程并生成大纲
  createProcess: async (data: CreateProcessInput): Promise<ProcessCreationResponse> => {
    try {
      console.log('发送创建请求:', data);
      const response = await apiClient.post('/api/process/start', data);
      return response.data;
    } catch (error) {
      console.error('创建过程失败:', error);
      throw error;
    }
  },

  // 更新大纲
  updateOutline: async (processId: string, data: OutlineUpdateRequest): Promise<OutlineUpdateResponse> => {
    const response = await apiClient.post(`/api/process/${processId}/outline`, data);
    return response.data;
  },

  // 开始检索
  startRetrieval: async (processId: string, data: RetrievalStartRequest): Promise<RetrievalStartResponse> => {
    const response = await apiClient.post(`/api/process/${processId}/retrieval/start`, data);
    return response.data;
  },

  // 获取检索状态
  getRetrievalStatus: async (processId: string): Promise<RetrievalStatusResponse> => {
    const response = await apiClient.get(`/api/process/${processId}/retrieval/status`);
    return response.data;
  },

  // 开始生成文章
  startComposition: async (processId: string): Promise<CompositionStartResponse> => {
    const response = await apiClient.post(`/api/process/${processId}/compose/start`);
    return response.data;
  },

  // 获取文章内容
  getArticle: async (processId: string): Promise<ArticleResponse> => {
    const response = await apiClient.get(`/api/process/${processId}/article`);
    return response.data;
  },
};

export default apiService; 