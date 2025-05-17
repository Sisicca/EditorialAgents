import { create } from 'zustand';
import type { OutlineNode, RetrievalOverallStatus } from '../services/api';

interface ProcessState {
  // 当前流程ID
  currentProcessId: string | null;
  // 当前主题
  currentTopic: string | null;
  // 大纲数据
  outline: OutlineNode | null;
  // 检索状态
  retrievalStatus: RetrievalOverallStatus | null;
  // 文章状态
  compositionStatus: string | null;
  // 文章内容
  articleContent: string | null;
  // 设置当前流程ID
  setCurrentProcessId: (id: string | null) => void;
  // 设置当前主题
  setCurrentTopic: (topic: string | null) => void;
  // 设置大纲
  setOutline: (outline: OutlineNode | null) => void;
  // 设置检索状态
  setRetrievalStatus: (status: RetrievalOverallStatus | null) => void;
  // 设置文章状态
  setCompositionStatus: (status: string | null) => void;
  // 设置文章内容
  setArticleContent: (content: string | null) => void;
  // 重置所有状态
  resetState: () => void;
}

// 创建状态存储
const useProcessStore = create<ProcessState>((set) => ({
  currentProcessId: null,
  currentTopic: null,
  outline: null,
  retrievalStatus: null,
  compositionStatus: null,
  articleContent: null,

  setCurrentProcessId: (id) => set({ currentProcessId: id }),
  setCurrentTopic: (topic) => set({ currentTopic: topic }),
  setOutline: (outline) => set({ outline }),
  setRetrievalStatus: (status) => set({ retrievalStatus: status }),
  setCompositionStatus: (status) => set({ compositionStatus: status }),
  setArticleContent: (content) => set({ articleContent: content }),
  
  resetState: () => set({
    currentProcessId: null,
    currentTopic: null,
    outline: null,
    retrievalStatus: null,
    compositionStatus: null,
    articleContent: null,
  }),
}));

export default useProcessStore; 