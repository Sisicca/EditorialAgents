import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { 
  Box, 
  Heading, 
  Text, 
  FormControl, 
  FormLabel, 
  Input, 
  Textarea, 
  Button, 
  Stack,
  useToast,
  FormErrorMessage
} from '@chakra-ui/react';
import apiService from '../services/api';
import type { CreateProcessInput } from '../services/api';
import useProcessStore from '../store/processStore';

const InputPage = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const { setCurrentProcessId, setCurrentTopic, setOutline } = useProcessStore();

  // 表单状态
  const [formData, setFormData] = useState<CreateProcessInput>({
    topic: '',
    description: '',
    problem: ''
  });

  // 表单错误状态
  const [errors, setErrors] = useState({
    topic: ''
  });

  // 表单输入变更
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // 清除错误
    if (name === 'topic' && value.trim()) {
      setErrors(prev => ({ ...prev, topic: '' }));
    }
  };

  // API调用
  const createProcessMutation = useMutation({
    mutationFn: (data: CreateProcessInput) => apiService.createProcess(data),
    onSuccess: (response) => {
      console.log('创建大纲成功，收到响应:', response);
      
      // 更新全局状态
      setCurrentProcessId(response.process_id);
      setCurrentTopic(response.topic);
      setOutline(response.initial_outline);
      
      console.log('全局状态已更新:', {
        processId: response.process_id,
        topic: response.topic,
        outline: response.initial_outline
      });
      
      toast({
        title: '创建成功',
        description: '已成功创建新项目并生成大纲',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      
      // 导航到大纲页面
      navigate(`/outline/${response.process_id}`);
    },
    onError: (error: any) => {
      console.error('API错误:', error);
      toast({
        title: '创建失败',
        description: error.message || '无法创建新项目，请重试',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  });

  // 表单提交
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // 验证
    let valid = true;
    const newErrors = { topic: '' };
    
    if (!formData.topic.trim()) {
      newErrors.topic = '主题不能为空';
      valid = false;
    }
    
    if (!valid) {
      setErrors(newErrors);
      return;
    }

    console.log('提交表单:', formData);
    createProcessMutation.mutate(formData);
  };

  return (
    <Box py={10} maxW="800px" mx="auto">
      <Heading mb={6}>创建新文章</Heading>
      
      <form onSubmit={handleSubmit}>
        <Stack spacing={6} bg="white" p={6} borderRadius="md" boxShadow="md">
          <FormControl isRequired isInvalid={!!errors.topic}>
            <FormLabel>文章主题</FormLabel>
            <Input 
              name="topic"
              value={formData.topic}
              onChange={handleInputChange}
              placeholder="例如：人工智能在教育领域的应用" 
            />
            {errors.topic && <FormErrorMessage>{errors.topic}</FormErrorMessage>}
          </FormControl>
          
          <FormControl>
            <FormLabel>主题描述（可选）</FormLabel>
            <Textarea 
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              placeholder="请详细描述您的主题内容..." 
            />
          </FormControl>
          
          <FormControl>
            <FormLabel>核心问题（可选）</FormLabel>
            <Textarea 
              name="problem"
              value={formData.problem}
              onChange={handleInputChange}
              placeholder="您希望在文章中解答的核心问题..." 
            />
          </FormControl>
          
          <Button 
            type="submit"
            colorScheme="green" 
            size="lg" 
            alignSelf="flex-start"
            isLoading={createProcessMutation.isPending}
            loadingText="正在创建..."
          >
            创建并生成大纲
          </Button>
        </Stack>
      </form>
    </Box>
  );
};

export default InputPage; 