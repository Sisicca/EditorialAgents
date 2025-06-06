import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { 
  Box, 
  Heading, 
  Text, 
  Divider, 
  Stack, 
  Button, 
  Spinner,
  Alert,
  AlertIcon,
  useToast,
  Flex,
  Progress
} from '@chakra-ui/react';
import apiService from '../services/api';
import type { ArticleResponse } from '../services/api';
import useProcessStore from '../store/processStore';

const ArticlePage = () => {
  const { processId } = useParams<{ processId: string }>();
  const navigate = useNavigate();
  const toast = useToast();
  const { 
    currentProcessId, 
    setCurrentProcessId, 
    articleContent, 
    setArticleContent,
    setCompositionStatus
  } = useProcessStore();

  // 如果没有processId，重定向到首页
  useEffect(() => {
    if (!processId) {
      navigate('/');
    } else if (processId !== currentProcessId) {
      setCurrentProcessId(processId);
    }
  }, [processId, navigate, currentProcessId, setCurrentProcessId]);

  // 开始文章生成的Mutation
  const startCompositionMutation = useMutation({
    mutationFn: () => apiService.startComposition(processId!),
    onSuccess: (response) => {
      console.log('文章生成已启动:', response);
      toast({
        title: "文章生成已启动",
        description: response.message,
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      
      // 重新获取文章状态
      articleQuery.refetch();
    },
    onError: (error: any) => {
      console.error('启动文章生成失败:', error);
      toast({
        title: "启动文章生成失败",
        description: error.message,
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    }
  });

  // 获取文章内容和状态
  const articleQuery = useQuery({
    queryKey: ['article', processId],
    queryFn: () => apiService.getArticle(processId!),
    enabled: !!processId,
    refetchInterval: (data: unknown) => {
      // 使用明确类型
      const articleData = data as ArticleResponse | undefined;
      // 如果文章已完成或出错，停止轮询
      if (articleData?.composition_status === 'Completed' || 
          articleData?.composition_status === 'Error') {
        return false;
      }
      // 否则每3秒轮询一次
      return 3000;
    }
  });

  // 文章数据变化时更新全局状态
  useEffect(() => {
    if (articleQuery.data) {
      const data = articleQuery.data as ArticleResponse;
      console.log('文章状态:', data);
      setCompositionStatus(data.composition_status);
      if (data.article_content) {
        setArticleContent(data.article_content);
      }
    }
  }, [articleQuery.data, setCompositionStatus, setArticleContent]);

  // 导出为PDF（示例功能，实际需要后端支持）
  const handleExportPDF = () => {
    toast({
      title: "导出功能",
      description: "PDF导出功能正在开发中",
      status: "info",
      duration: 3000,
      isClosable: true,
    });
  };

  // 导出为Markdown（示例功能，实际需要后端支持）
  const handleExportMarkdown = () => {
    toast({
      title: "导出功能",
      description: "Markdown导出功能正在开发中",
      status: "info",
      duration: 3000,
      isClosable: true,
    });
  };

  // 开始生成文章
  const handleStartComposition = () => {
    if (!processId) return;
    startCompositionMutation.mutate();
  };

  // 如果正在加载初始数据
  if (articleQuery.isLoading) {
    return (
      <Box py={10} maxW="800px" mx="auto" textAlign="center">
        <Spinner size="xl" color="green.500" thickness="4px" />
        <Text mt={4}>加载文章数据...</Text>
      </Box>
    );
  }

  // 如果文章数据加载失败
  if (articleQuery.isError) {
    return (
      <Box py={10} maxW="800px" mx="auto">
        <Alert status="error" borderRadius="md">
          <AlertIcon />
          无法加载文章数据，请重试
        </Alert>
        <Button mt={4} onClick={() => articleQuery.refetch()}>重新加载</Button>
        <Button mt={4} ml={2} onClick={() => navigate(`/retrieval/${processId}`)}>返回检索页面</Button>
      </Box>
    );
  }

  // 获取文章状态和内容 - 使用类型断言
  const data = articleQuery.data as ArticleResponse;
  const status = data?.composition_status || 'Not Started';
  // 获取文章内容
  const content = data?.article_content || articleContent || '';

  // 文章内容 - 仅在已完成状态或有内容且非生成中状态下显示
  const shouldShowContent = status === 'Completed' || (!!content && status !== 'In Progress');

  return (
    <Box py={10} maxW="800px" mx="auto">
      <Heading mb={6}>最终文章</Heading>
      
      {/* 文章生成状态和控制 */}
      {(status === 'Not Started' || status === 'Error') && (
        <Box mb={6} p={4} bg="white" borderRadius="md" boxShadow="md">
          <Heading size="md" mb={4}>开始生成文章</Heading>
          <Text mb={4}>
            您已完成检索阶段，现在可以开始生成最终文章了。
            {status === 'Error' && (
              <Alert status="error" mt={2}>
                <AlertIcon />
                上次文章生成过程中出现错误，请重试。
              </Alert>
            )}
          </Text>
          <Button 
            colorScheme="green" 
            size="lg" 
            onClick={handleStartComposition}
            isLoading={startCompositionMutation.isPending}
            loadingText="正在启动..."
          >
            开始生成文章
          </Button>
        </Box>
      )}
      
      {/* 等待中 - 确保在状态为"In Progress"或包含具体状态信息时总是显示等待动画 */}
      {(status === 'In Progress' || (status && status.includes('正在'))) && (
        <Box mb={6} p={6} bg="white" borderRadius="md" boxShadow="md" textAlign="center">
          <Heading size="md" mb={4}>文章生成中</Heading>
          <Box position="relative" my={8}>
            <Spinner 
              size="xl" 
              color="green.500" 
              thickness="4px" 
              speed="0.8s"
              emptyColor="gray.200"
            />
            <Box 
              position="absolute" 
              top="50%" 
              left="50%" 
              transform="translate(-50%, -50%)" 
              fontSize="sm" 
              color="green.600"
            >
              {/* 显示具体的生成状态，如果没有具体状态则显示默认文本 */}
              {status && status.includes('正在') ? status : 'AI思考中'}
            </Box>
          </Box>
          
          <Progress 
            hasStripe 
            isAnimated 
            colorScheme="green" 
            size="sm" 
            value={status && status.includes('引言和结论') ? 90 : status && status.includes('整理文章格式') ? 95 : 70} 
            borderRadius="md"
            mb={4}
          />
          
          <Stack spacing={4} mt={6} maxW="md" mx="auto">
            <Text fontWeight="medium">
              {status && status.includes('正在') ? 
                `${status}，请耐心等待...` : 
                'AI正在创作您的文章，请耐心等待...'
              }
            </Text>
            <Text fontSize="sm" color="gray.600">
              根据文章复杂度，完成时间约为1-3分钟
            </Text>
            <Text fontSize="sm" color="gray.500" fontStyle="italic">
              {status && status.includes('主体内容') ? 'AI正在分析检索数据，整合观点，生成主体内容' :
               status && status.includes('引言和结论') ? 'AI正在基于主体内容生成引言和结论' :
               status && status.includes('整理文章格式') ? 'AI正在整理文章格式和参考文献' :
               'AI正在分析检索数据，整合观点，生成流畅的文章内容'
              }
            </Text>
          </Stack>
          
          {articleQuery.isFetching && (
            <Text mt={4} fontSize="sm" color="blue.500">
              正在获取最新状态...
            </Text>
          )}
        </Box>
      )}
      
      {/* 文章内容 - 仅在已完成状态或有内容且非生成中状态下显示 */}
      {shouldShowContent && (
        <Box bg="white" p={8} borderRadius="md" boxShadow="md">
          {data?.article_content ? (
            <>
              <Text color="gray.600" mb={6}>
                状态: {status === 'Completed' ? '已完成' : '生成中...'}
              </Text>
              
              <Divider mb={6} />
              
              <Stack spacing={6}>
                {/* 这里使用dangerouslySetInnerHTML是为了支持文章内容中的换行符转换为HTML */}
                <div dangerouslySetInnerHTML={{ __html: content.replace(/\n/g, '<br>') }} />
              </Stack>
            </>
          ) : (
            <Text>文章内容尚未生成</Text>
          )}
        </Box>
      )}
      
      {/* 导出按钮 - 仅在文章完成时显示 */}
      {status === 'Completed' && content && (
        <Stack direction="row" spacing={4} mt={6}>
          <Button colorScheme="green" onClick={handleExportPDF}>导出为PDF</Button>
          <Button variant="outline" onClick={handleExportMarkdown}>导出为Markdown</Button>
        </Stack>
      )}
      
      {/* 导航按钮 */}
      <Flex mt={6} justify="flex-start">
        <Button 
          variant="outline" 
          onClick={() => navigate(`/retrieval/${processId}`)}
        >
          返回检索页面
        </Button>
      </Flex>
    </Box>
  );
};

export default ArticlePage;