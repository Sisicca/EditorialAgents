import { Box, Heading, Text, Button, Stack } from '@chakra-ui/react';
import { Link } from 'react-router-dom';

const HomePage = () => {
  return (
    <Box py={10} maxW="800px" mx="auto">
      <Stack spacing={6}>
        <Heading as="h1" size="xl" color="green.600">
          AI 编辑助手
        </Heading>
        
        <Text fontSize="lg">
          利用先进的AI技术，助您创作出高质量的文章内容。从大纲规划到资料收集，再到文章成型，全流程智能辅助。
        </Text>
        
        <Box>
          <Link to="/input">
            <Button colorScheme="green" size="lg">
              开始创作
            </Button>
          </Link>
        </Box>
        
        <Box mt={12}>
          <Heading as="h2" size="lg" mb={6}>
            如何工作
          </Heading>
          
          <Stack spacing={4}>
            <Box p={4} bg="white" borderRadius="md" boxShadow="sm">
              <Heading size="md" mb={2} color="green.500">1. 确定主题</Heading>
              <Text>输入您想要创作的文章主题、描述和核心问题，AI将为您生成初步大纲。</Text>
            </Box>
            
            <Box p={4} bg="white" borderRadius="md" boxShadow="sm">
              <Heading size="md" mb={2} color="green.500">2. 完善大纲</Heading>
              <Text>编辑和调整大纲结构，添加、删除或修改章节，直到满意为止。</Text>
            </Box>
            
            <Box p={4} bg="white" borderRadius="md" boxShadow="sm">
              <Heading size="md" mb={2} color="green.500">3. 智能检索</Heading>
              <Text>系统会为每个章节自动检索相关资料，从互联网和知识库中获取信息。</Text>
            </Box>
            
            <Box p={4} bg="white" borderRadius="md" boxShadow="sm">
              <Heading size="md" mb={2} color="green.500">4. 成文生成</Heading>
              <Text>基于大纲和检索资料，AI将生成结构清晰、内容丰富的完整文章。</Text>
            </Box>
          </Stack>
        </Box>
      </Stack>
    </Box>
  );
};

export default HomePage; 