import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Box, 
  Heading, 
  Text, 
  Button, 
  Stack, 
  Card, 
  CardBody, 
  Textarea,
  IconButton,
  Flex,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  FormControl,
  FormLabel,
  Input,
} from '@chakra-ui/react';
import { ChevronDownIcon, ChevronUpIcon, AddIcon, DeleteIcon, EditIcon } from '@chakra-ui/icons';
import useProcessStore from '../store/processStore';
import apiService from '../services/api';
import type { OutlineNode, OutlineUpdateRequest } from '../services/api';
import { useMutation, useQuery } from '@tanstack/react-query';

// 生成唯一ID
const generateNodeId = () => {
  return `node-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
};

// 递归渲染单个大纲节点
const OutlineNodeComponent = ({ 
  node, 
  onUpdate, 
  onAddChild,
  onDelete,
  level = 0,
  path = [] 
}: { 
  node: OutlineNode, 
  onUpdate: (updatedNode: OutlineNode, path: number[]) => void,
  onAddChild: (parentId: string) => void,
  onDelete: (nodeId: string, path: number[]) => void,
  level?: number,
  path?: number[]
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedTitle, setEditedTitle] = useState(node.title);
  const [editedSummary, setEditedSummary] = useState(node.summary || '');

  const handleTitleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setEditedTitle(e.target.value);
  };

  const handleSummaryChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setEditedSummary(e.target.value);
  };

  const saveChanges = () => {
    const updatedNode = {
      ...node,
      title: editedTitle,
      summary: editedSummary,
    };
    onUpdate(updatedNode, path);
    setIsEditing(false);
  };

  return (
    <Card mb={4} borderLeftWidth="4px" borderLeftColor="green.400">
      <CardBody>
        {isEditing ? (
          <Stack spacing={4}>
            <Textarea
              value={editedTitle}
              onChange={handleTitleChange}
              placeholder="章节标题"
              size="md"
              fontWeight="bold"
            />
            <Textarea
              value={editedSummary}
              onChange={handleSummaryChange}
              placeholder="章节摘要"
              size="md"
              rows={4}
            />
            <Flex gap={2}>
              <Button size="sm" colorScheme="green" onClick={saveChanges}>保存</Button>
              <Button size="sm" variant="outline" onClick={() => setIsEditing(false)}>取消</Button>
            </Flex>
          </Stack>
        ) : (
          <>
            <Flex justify="space-between" align="center" mb={2}>
              <Heading size="md">{node.title}</Heading>
              <Flex>
                <IconButton
                  aria-label="添加子章节"
                  icon={<AddIcon />}
                  size="sm"
                  variant="ghost"
                  mr={2}
                  onClick={() => onAddChild(node.id)}
                />
                <IconButton
                  aria-label="编辑章节"
                  icon={<EditIcon />}
                  size="sm"
                  variant="ghost"
                  mr={2}
                  onClick={() => setIsEditing(true)}
                />
                <IconButton
                  aria-label="删除章节"
                  icon={<DeleteIcon />}
                  size="sm"
                  variant="ghost"
                  colorScheme="red"
                  onClick={() => onDelete(node.id, path)}
                />
              </Flex>
            </Flex>
            {node.summary && <Text color="gray.600" mb={4}>{node.summary}</Text>}
          </>
        )}

        {node.children && node.children.length > 0 && (
          <Box ml={4} mt={4} borderLeftWidth="1px" borderLeftColor="gray.200" pl={4}>
            {node.children.map((child, index) => (
              <OutlineNodeComponent
                key={child.id}
                node={child}
                onUpdate={onUpdate}
                onAddChild={onAddChild}
                onDelete={onDelete}
                level={level + 1}
                path={[...path, index]}
              />
            ))}
          </Box>
        )}
      </CardBody>
    </Card>
  );
};

const OutlinePage = () => {
  const { processId } = useParams<{ processId: string }>();
  const navigate = useNavigate();
  const toast = useToast();
  const { 
    outline, 
    setOutline, 
    currentTopic, 
    setCurrentTopic, 
    currentProcessId, 
    setCurrentProcessId 
  } = useProcessStore();

  // 模态弹窗控制
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [newNodeParentId, setNewNodeParentId] = useState<string | null>(null);
  const [newNodeTitle, setNewNodeTitle] = useState('');
  const [newNodeSummary, setNewNodeSummary] = useState('');

  // 如果没有processId，重定向到首页
  useEffect(() => {
    if (!processId) {
      navigate('/');
    } else if (processId !== currentProcessId) {
      setCurrentProcessId(processId);
    }
  }, [processId, navigate, currentProcessId, setCurrentProcessId]);

  // 如果状态中没有大纲数据，从API获取
  const outlineQuery = useQuery({
    queryKey: ['outline', processId],
    queryFn: async () => {
      console.log('尝试从API加载大纲数据...');
      
      try {
        // 如果我们已经有数据，就不需要调用API
        if (outline && currentProcessId === processId) {
          console.log('使用已有的大纲数据');
          return outline;
        }
        
        // 我们可能需要一个新的API端点来获取大纲数据
        // 目前只能使用模拟数据或者临时解决方案
        console.log('无法从API获取大纲，当前没有获取单个大纲的API');
        return null;
      } catch (error) {
        console.error('获取大纲数据失败:', error);
        throw error;
      }
    },
    // 只有当processId存在且状态中没有大纲时才执行查询
    enabled: !!processId && (!outline || currentProcessId !== processId),
  });

  // 打印调试信息
  useEffect(() => {
    console.log('OutlinePage - 当前状态:', {
      processId,
      currentProcessId,
      outline,
      currentTopic
    });
  }, [processId, currentProcessId, outline, currentTopic]);

  // 更新大纲的mutation
  const updateOutlineMutation = useMutation({
    mutationFn: (data: OutlineUpdateRequest) => 
      apiService.updateOutline(processId!, data),
    onSuccess: () => {
      toast({
        title: "大纲已更新",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
    },
    onError: (error: any) => {
      toast({
        title: "更新失败",
        description: error.message || "无法更新大纲，请重试",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    },
  });

  // 更新节点处理函数
  const handleNodeUpdate = (updatedNode: OutlineNode, path: number[]) => {
    if (!outline) return;
    
    const newOutline = JSON.parse(JSON.stringify(outline)) as OutlineNode;
    
    // 递归更新节点
    const updateNodeAtPath = (node: OutlineNode, remainingPath: number[]): OutlineNode => {
      if (remainingPath.length === 0) {
        return updatedNode;
      }
      
      const index = remainingPath[0];
      const restPath = remainingPath.slice(1);
      
      if (!node.children || !node.children[index]) {
        return node;
      }
      
      const updatedChildren = [...node.children];
      updatedChildren[index] = updateNodeAtPath(node.children[index], restPath);
      
      return {
        ...node,
        children: updatedChildren,
      };
    };
    
    // 如果path为空，意味着我们在更新根节点
    const result = path.length === 0 
      ? updatedNode 
      : updateNodeAtPath(newOutline, path);
    
    setOutline(result);
  };

  // 处理添加章节
  const handleAddChildNode = (parentId: string) => {
    setNewNodeParentId(parentId);
    setNewNodeTitle('');
    setNewNodeSummary('');
    onOpen();
  };

  // 处理删除章节
  const handleDeleteNode = (nodeId: string, path: number[]) => {
    if (!outline) return;
    
    // 确认是否要删除
    if (!window.confirm('确定要删除此章节及其所有子章节吗？此操作不可撤销。')) {
      return;
    }

    const newOutline = JSON.parse(JSON.stringify(outline)) as OutlineNode;
    
    // 如果要删除的是顶级章节
    if (path.length === 0) {
      // 不应该删除根节点
      toast({
        title: "无法删除根节点",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    
    // 递归删除节点
    const deleteNodeAtPath = (node: OutlineNode, remainingPath: number[]): OutlineNode => {
      if (remainingPath.length === 1) {
        // 我们找到了父节点，从其子节点数组中删除目标节点
        const index = remainingPath[0];
        if (!node.children || !node.children[index]) {
          return node;
        }
        
        const updatedChildren = [...node.children];
        updatedChildren.splice(index, 1);
        
        return {
          ...node,
          children: updatedChildren,
        };
      }
      
      const index = remainingPath[0];
      const restPath = remainingPath.slice(1);
      
      if (!node.children || !node.children[index]) {
        return node;
      }
      
      const updatedChildren = [...node.children];
      updatedChildren[index] = deleteNodeAtPath(node.children[index], restPath);
      
      return {
        ...node,
        children: updatedChildren,
      };
    };
    
    const result = deleteNodeAtPath(newOutline, path);
    setOutline(result);
    
    toast({
      title: "章节已删除",
      status: "info",
      duration: 2000,
      isClosable: true,
    });
  };

  // 确认添加新章节
  const confirmAddNode = () => {
    if (!outline || !newNodeParentId) return;
    
    if (!newNodeTitle.trim()) {
      toast({
        title: "章节标题不能为空",
        status: "error",
        duration: 2000,
        isClosable: true,
      });
      return;
    }
    
    const newNode: OutlineNode = {
      id: generateNodeId(),
      title: newNodeTitle,
      summary: newNodeSummary,
      level: 0, // 将在添加过程中设置正确的level
      children: []
    };
    
    const newOutline = JSON.parse(JSON.stringify(outline)) as OutlineNode;
    
    // 添加到根节点
    if (newNodeParentId === newOutline.id) {
      newNode.level = newOutline.level + 1;
      if (!newOutline.children) {
        newOutline.children = [];
      }
      newOutline.children.push(newNode);
      setOutline(newOutline);
      onClose();
      return;
    }
    
    // 递归查找父节点并添加新节点
    let addedSuccessfully = false;
    
    const addNodeToParent = (node: OutlineNode): boolean => {
      if (node.id === newNodeParentId) {
        newNode.level = node.level + 1;
        if (!node.children) {
          node.children = [];
        }
        node.children.push(newNode);
        return true;
      }
      
      if (node.children && node.children.length > 0) {
        for (let i = 0; i < node.children.length; i++) {
          if (addNodeToParent(node.children[i])) {
            return true;
          }
        }
      }
      
      return false;
    };
    
    addedSuccessfully = addNodeToParent(newOutline);
    
    if (addedSuccessfully) {
      setOutline(newOutline);
      toast({
        title: "章节已添加",
        status: "success",
        duration: 2000,
        isClosable: true,
      });
    } else {
      toast({
        title: "添加失败",
        description: "无法找到父章节",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
    
    onClose();
  };

  // 添加顶级章节
  const handleAddTopLevelNode = () => {
    if (!outline) return;
    setNewNodeParentId(outline.id);
    setNewNodeTitle('');
    setNewNodeSummary('');
    onOpen();
  };

  // 保存大纲到服务器
  const handleSaveOutline = () => {
    if (!outline || !processId) return;
    
    const request: OutlineUpdateRequest = {
      outline_dict: outline
    };
    
    updateOutlineMutation.mutate(request);
  };

  // 渲染状态
  if (outlineQuery.isPending && !outline) {
    return (
      <Box py={10} maxW="800px" mx="auto" textAlign="center">
        <Spinner size="xl" color="green.500" thickness="4px" />
        <Text mt={4}>加载大纲数据...</Text>
      </Box>
    );
  }

  if (outlineQuery.isError && !outline) {
    return (
      <Box py={10} maxW="800px" mx="auto">
        <Alert status="error" borderRadius="md">
          <AlertIcon />
          无法加载大纲数据，请重试
        </Alert>
        <Button mt={4} onClick={() => navigate('/')}>返回首页</Button>
      </Box>
    );
  }

  // 确保我们有大纲数据
  const outlineData = outline;
  if (!outlineData) {
    return (
      <Box py={10} maxW="800px" mx="auto">
        <Alert status="warning" borderRadius="md">
          <AlertIcon />
          未找到大纲数据，可能需要重新创建
        </Alert>
        <Button mt={4} onClick={() => navigate('/input')}>创建新文章</Button>
      </Box>
    );
  }

  return (
    <Box py={10} maxW="800px" mx="auto">
      <Flex justify="space-between" align="center" mb={6}>
        <Heading>大纲编辑</Heading>
        <Flex gap={3}>
          <Button
            colorScheme="blue"
            leftIcon={<AddIcon />}
            onClick={handleAddTopLevelNode}
          >
            添加主章节
          </Button>
          <Button 
            colorScheme="green" 
            onClick={handleSaveOutline}
            isLoading={updateOutlineMutation.isPending}
            loadingText="保存中..."
          >
            保存大纲
          </Button>
        </Flex>
      </Flex>
      
      {currentTopic && (
        <Text fontSize="lg" fontWeight="medium" mb={6}>
          主题：{currentTopic}
        </Text>
      )}
      
      <OutlineNodeComponent 
        node={outlineData} 
        onUpdate={handleNodeUpdate}
        onAddChild={handleAddChildNode}
        onDelete={handleDeleteNode}
      />
      
      <Button 
        mt={6} 
        colorScheme="blue" 
        onClick={() => navigate(`/retrieval/${processId}`)}
      >
        进入检索阶段
      </Button>

      {/* 添加章节的模态框 */}
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>添加新章节</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <FormControl isRequired>
              <FormLabel>章节标题</FormLabel>
              <Input
                value={newNodeTitle}
                onChange={(e) => setNewNodeTitle(e.target.value)}
                placeholder="输入章节标题"
              />
            </FormControl>
            <FormControl mt={4}>
              <FormLabel>章节摘要 (可选)</FormLabel>
              <Textarea
                value={newNodeSummary}
                onChange={(e) => setNewNodeSummary(e.target.value)}
                placeholder="输入章节摘要"
              />
            </FormControl>
          </ModalBody>
          <ModalFooter>
            <Button variant="outline" mr={3} onClick={onClose}>
              取消
            </Button>
            <Button colorScheme="blue" onClick={confirmAddNode}>
              添加
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default OutlinePage; 