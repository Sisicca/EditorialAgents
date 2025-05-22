import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { 
  Box, 
  Heading, 
  Text, 
  Progress, 
  Stack, 
  Card, 
  CardBody, 
  Badge, 
  Button, 
  Checkbox,
  FormControl,
  FormLabel,
  Spinner,
  Alert,
  AlertIcon,
  useToast,
  Flex,
  Collapse,
  useDisclosure,
  IconButton
} from '@chakra-ui/react';
import { ChevronDownIcon, ChevronUpIcon } from '@chakra-ui/icons';
import apiService from '../services/api';
import type { RetrievalStartRequest, LeafNodeStatus } from '../services/api';
import useProcessStore from '../store/processStore';

// 单个节点状态组件
const RetrievalNodeStatus = ({ nodeStatus }: { nodeStatus: LeafNodeStatus }) => {
  const { isOpen, onToggle } = useDisclosure();
  const { isOpen: isQueriesOpen, onToggle: onQueriesToggle } = useDisclosure();
  
  // 根据状态选择徽章颜色
  const getBadgeColor = () => {
    if (nodeStatus.is_completed) return 'green';
    if (nodeStatus.error_message) return 'red';
    return 'yellow';
  };
  
  // 状态显示文本
  const getStatusText = () => {
    if (nodeStatus.is_completed) return '已完成';
    if (nodeStatus.error_message) return '错误';
    return '检索中';
  };
  
  // 显示检索到的文档数量
  const getDocumentsCount = () => {
    return nodeStatus.retrieved_docs_preview?.length || 0;
  };
  
  // 将逗号分隔的查询语句转换为数组
  const getQueriesArray = () => {
    if (!nodeStatus.current_query) return [];
    return nodeStatus.current_query.split(',').map(q => q.trim()).filter(q => q);
  };
  
  return (
    <Card mb={4}>
      <CardBody>
        <Flex justify="space-between" align="center" mb={2}>
          <Heading size="md">{nodeStatus.title}</Heading>
          <Flex>
            <Badge colorScheme={getBadgeColor()} mr={2}>
              {getStatusText()}
            </Badge>
          </Flex>
        </Flex>
        
        <Text>
          {nodeStatus.is_completed 
            ? `已检索到${getDocumentsCount()}个文档，内容已生成` 
            : nodeStatus.status_message || '等待检索...'}
        </Text>
        
        {!nodeStatus.is_completed && !nodeStatus.error_message && (
          <Progress size="sm" mt={2} isIndeterminate colorScheme="yellow" />
        )}
        
        {nodeStatus.error_message && (
          <Alert status="error" mt={2} size="sm">
            <AlertIcon />
            {nodeStatus.error_message}
          </Alert>
        )}
        
        {/* 内容预览 - 单独显示，不在折叠区域内 */}
        {nodeStatus.content_preview && (
          <Box mt={4} p={4} bg="blue.50" borderRadius="md">
            <Text fontWeight="bold" mb={2} fontSize="md">内容预览:</Text>
            <Box 
              p={3} 
              bg="white" 
              borderRadius="md" 
              boxShadow="sm"
              maxH="none" 
              overflow="auto"
              whiteSpace="pre-wrap"
            >
              <Text>{nodeStatus.content_preview}</Text>
            </Box>
          </Box>
        )}
        
        {/* 检索语句竖向显示 */}
        {nodeStatus.current_query && (
          <Box mt={4}>
            <Flex 
              justify="space-between" 
              align="center" 
              onClick={onQueriesToggle} 
              cursor="pointer"
              p={2}
              bg="blue.50"
              borderRadius="md"
              _hover={{ bg: "blue.100" }}
            >
              <Text fontWeight="bold">检索语句 ({getQueriesArray().length})</Text>
              <IconButton
                aria-label="显示检索语句"
                icon={isQueriesOpen ? <ChevronUpIcon /> : <ChevronDownIcon />}
                size="sm"
                variant="ghost"
              />
            </Flex>
            
            <Collapse in={isQueriesOpen} animateOpacity>
              <Stack mt={2} pl={4} spacing={2}>
                {getQueriesArray().map((query, index) => (
                  <Box 
                    key={index} 
                    p={2} 
                    bg="gray.50" 
                    borderRadius="md" 
                    borderLeft="3px solid" 
                    borderLeftColor="blue.400"
                  >
                    <Text fontSize="sm">{query}</Text>
                  </Box>
                ))}
              </Stack>
            </Collapse>
          </Box>
        )}
        
        {/* 检索文档可折叠区域 */}
        {nodeStatus.retrieved_docs_preview && nodeStatus.retrieved_docs_preview.length > 0 && (
          <Box mt={4}>
            <Flex 
              justify="space-between" 
              align="center" 
              onClick={onToggle} 
              cursor="pointer"
              p={2}
              bg="green.50"
              borderRadius="md"
              _hover={{ bg: "green.100" }}
            >
              <Text fontWeight="bold">
                检索文档 ({nodeStatus.retrieved_docs_preview.length})
              </Text>
              <IconButton
                aria-label="显示详情"
                icon={isOpen ? <ChevronUpIcon /> : <ChevronDownIcon />}
                size="sm"
                variant="ghost"
              />
            </Flex>
            
            <Collapse in={isOpen} animateOpacity>
              <Box mt={2} p={3} bg="gray.50" borderRadius="md">
                <Stack>
                  {nodeStatus.retrieved_docs_preview.map(doc => (
                    <Box key={doc.id} fontSize="sm" p={2} bg="white" borderRadius="sm">
                      <Text fontWeight="bold">{doc.title || doc.citation_key}</Text>
                      <Text>来源: {doc.source}</Text>
                    </Box>
                  ))}
                </Stack>
              </Box>
            </Collapse>
          </Box>
        )}
      </CardBody>
    </Card>
  );
};

const RetrievalPage = () => {
  const { processId } = useParams<{ processId: string }>();
  const navigate = useNavigate();
  const toast = useToast();
  const { currentProcessId, setCurrentProcessId } = useProcessStore();
  
  // 检索选项状态
  const [useWebSearch, setUseWebSearch] = useState(true);
  const [useKbSearch, setUseKbSearch] = useState(true);
  
  // 如果没有processId，重定向到首页
  useEffect(() => {
    if (!processId) {
      navigate('/');
    } else if (processId !== currentProcessId) {
      setCurrentProcessId(processId);
    }
  }, [processId, navigate, currentProcessId, setCurrentProcessId]);
  
  // 开始检索的mutation
  const startRetrievalMutation = useMutation({
    mutationFn: (data: RetrievalStartRequest) => 
      apiService.startRetrieval(processId!, data),
    onSuccess: (response) => {
      console.log('检索已启动:', response);
      toast({
        title: "检索已启动",
        description: response.message,
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      
      // 重新获取检索状态
      retrievalStatusQuery.refetch();
    },
    onError: (error: any) => {
      console.error('启动检索失败:', error);
      toast({
        title: "启动检索失败",
        description: error.message,
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    }
  });
  
  // 获取检索状态
  const retrievalStatusQuery = useQuery({
    queryKey: ['retrievalStatus', processId],
    queryFn: () => apiService.getRetrievalStatus(processId!),
    enabled: !!processId,
    refetchInterval: 3000, // 每3秒轮询一次
  });
  
  // 处理开始检索
  const handleStartRetrieval = () => {
    if (!processId) return;
    
    const request: RetrievalStartRequest = {
      use_web: useWebSearch,
      use_kb: useKbSearch
    };
    
    startRetrievalMutation.mutate(request);
  };
  
  // 处理进入文章页面
  const handleGoToArticle = () => {
    if (!processId) return;
    navigate(`/article/${processId}`);
  };
  
  // 检查检索是否完成
  const isRetrievalCompleted = () => {
    const status = retrievalStatusQuery.data?.retrieval_status;
    return status && 
           status.completed_leaf_nodes === status.total_leaf_nodes && 
           status.total_leaf_nodes > 0;
  };
  
  // 计算完成百分比
  const getCompletionPercentage = () => {
    const status = retrievalStatusQuery.data?.retrieval_status;
    if (!status || status.total_leaf_nodes === 0) return 0;
    return (status.completed_leaf_nodes / status.total_leaf_nodes) * 100;
  };
  
  // 如果正在加载初始数据
  if (retrievalStatusQuery.isLoading) {
    return (
      <Box py={10} maxW="800px" mx="auto" textAlign="center">
        <Spinner size="xl" color="green.500" thickness="4px" />
        <Text mt={4}>加载检索状态...</Text>
      </Box>
    );
  }
  
  // 如果检索状态加载失败
  if (retrievalStatusQuery.isError) {
    return (
      <Box py={10} maxW="800px" mx="auto">
        <Alert status="error" borderRadius="md">
          <AlertIcon />
          无法加载检索状态，请重试
        </Alert>
        <Button mt={4} onClick={() => retrievalStatusQuery.refetch()}>重新加载</Button>
        <Button mt={4} ml={2} onClick={() => navigate(`/outline/${processId}`)}>返回大纲</Button>
      </Box>
    );
  }
  
  // 获取叶节点状态数组
  const getLeafNodesArray = () => {
    const status = retrievalStatusQuery.data?.retrieval_status;
    if (!status || !status.leaf_nodes_status) return [];
    
    return Object.values(status.leaf_nodes_status);
  };

  return (
    <Box py={10} maxW="800px" mx="auto">
      <Heading mb={6}>检索进度</Heading>
      
      {!retrievalStatusQuery.data || !retrievalStatusQuery.data.retrieval_status.start_time ? (
        // 检索尚未开始，显示选项
        <Box mb={8} p={6} bg="white" borderRadius="md" boxShadow="md">
          <Heading size="md" mb={4}>开始检索</Heading>
          
          <Stack spacing={4}>
            <FormControl display="flex" alignItems="center">
              <Checkbox 
                isChecked={useWebSearch}
                onChange={(e) => setUseWebSearch(e.target.checked)}
                id="useWebSearch"
                colorScheme="green"
                size="lg"
              />
              <FormLabel htmlFor="useWebSearch" mb="0" ml={2}>
                使用网络检索
              </FormLabel>
            </FormControl>
            
            <FormControl display="flex" alignItems="center">
              <Checkbox 
                isChecked={useKbSearch}
                onChange={(e) => setUseKbSearch(e.target.checked)}
                id="useKbSearch"
                colorScheme="green"
                size="lg"
              />
              <FormLabel htmlFor="useKbSearch" mb="0" ml={2}>
                使用知识库检索
              </FormLabel>
            </FormControl>
            
            <Button 
              colorScheme="green" 
              size="lg" 
              onClick={handleStartRetrieval}
              isLoading={startRetrievalMutation.isPending}
              loadingText="正在启动..."
              isDisabled={!useWebSearch && !useKbSearch}
            >
              开始检索
            </Button>
          </Stack>
        </Box>
      ) : (
        // 检索已开始，显示进度
        <Box mb={8}>
          <Flex justify="space-between" align="center" mb={2}>
            <Text>
              整体进度: {retrievalStatusQuery.data?.retrieval_status.completed_leaf_nodes} / 
              {retrievalStatusQuery.data?.retrieval_status.total_leaf_nodes} 节点完成
            </Text>
            {retrievalStatusQuery.isFetching && (
              <Badge colorScheme="blue">更新中...</Badge>
            )}
          </Flex>
          <Progress 
            value={getCompletionPercentage()} 
            colorScheme="green"
            mb={2}
          />
          <Text fontSize="sm" color="gray.600">
            {retrievalStatusQuery.data?.retrieval_status.overall_status_message}
          </Text>
        </Box>
      )}
      
      {/* 检索节点状态列表 */}
      <Stack spacing={4}>
        {getLeafNodesArray().map((nodeStatus) => (
          <RetrievalNodeStatus key={nodeStatus.node_id} nodeStatus={nodeStatus} />
        ))}
      </Stack>
      
      {/* 导航按钮 */}
      <Flex mt={6} justify="space-between">
        <Button 
          variant="outline" 
          onClick={() => navigate(`/outline/${processId}`)}
        >
          返回大纲
        </Button>
        
        <Button 
          colorScheme="blue" 
          onClick={handleGoToArticle}
          isDisabled={!isRetrievalCompleted()}
        >
          {isRetrievalCompleted() ? '生成文章' : '等待检索完成后生成文章'}
        </Button>
      </Flex>
    </Box>
  );
};

export default RetrievalPage; 