import { Box, VStack, Heading, Text, Icon, Link, HStack, Divider } from '@chakra-ui/react';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import { FiHome, FiEdit, FiList, FiSearch, FiFileText, FiPlusCircle } from 'react-icons/fi';
import useProcessStore from '../../store/processStore';

const Sidebar = () => {
  const { pathname } = useLocation();
  const { currentProcessId, currentTopic } = useProcessStore();
  
  // 检查当前路径是否匹配
  const isActive = (path: string) => pathname === path || pathname.startsWith(path);
  
  // 边栏链接样式
  const linkStyle = (active: boolean) => ({
    display: 'flex',
    alignItems: 'center',
    p: 3,
    borderRadius: 'md',
    fontWeight: active ? 'semibold' : 'normal',
    bg: active ? 'green.50' : 'transparent',
    color: active ? 'green.600' : 'gray.600',
    _hover: {
      bg: active ? 'green.50' : 'gray.50',
      color: active ? 'green.600' : 'gray.700',
    },
    transition: 'all 0.2s',
  });

  return (
    <Box
      position="fixed"
      left={0}
      top={0}
      h="100vh"
      w={{ base: 'full', md: '250px' }}
      bg="white"
      borderRightWidth="1px"
      borderRightColor="gray.200"
      display={{ base: 'none', md: 'block' }}
      px={4}
      py={6}
      overflowY="auto"
    >
      <VStack align="stretch" spacing={6}>
        {/* 标题和应用名 */}
        <Box textAlign="center" mb={4}>
          <Heading as="h1" fontSize="xl" color="green.600" fontFamily="serif">
            AI 编辑助手
          </Heading>
          <Text fontSize="sm" color="gray.500" mt={1}>
            智能文章生成系统
          </Text>
        </Box>
        
        <Divider />
        
        {/* 主导航 */}
        <VStack align="stretch" spacing={1}>
          <Link
            as={RouterLink}
            to="/"
            {...linkStyle(isActive('/'))}
          >
            <HStack spacing={3}>
              <Icon as={FiHome} fontSize="lg" />
              <Text>主页</Text>
            </HStack>
          </Link>
          
          <Link
            as={RouterLink}
            to="/input"
            {...linkStyle(isActive('/input'))}
          >
            <HStack spacing={3}>
              <Icon as={FiPlusCircle} fontSize="lg" />
              <Text>新建文章</Text>
            </HStack>
          </Link>
        </VStack>
        
        {/* 当前流程导航，只有在有流程ID时显示 */}
        {currentProcessId && (
          <>
            <Divider />
            
            <Box>
              <Text fontSize="xs" fontWeight="medium" color="gray.500" textTransform="uppercase" mb={2} px={3}>
                当前文章
              </Text>
              {currentTopic && (
                <Text fontSize="sm" fontWeight="medium" color="gray.700" mb={3} px={3} noOfLines={2}>
                  {currentTopic}
                </Text>
              )}
              
              <VStack align="stretch" spacing={1}>
                <Link
                  as={RouterLink}
                  to={`/outline/${currentProcessId}`}
                  {...linkStyle(isActive(`/outline/${currentProcessId}`))}
                >
                  <HStack spacing={3}>
                    <Icon as={FiList} fontSize="lg" />
                    <Text>大纲编辑</Text>
                  </HStack>
                </Link>
                
                <Link
                  as={RouterLink}
                  to={`/retrieval/${currentProcessId}`}
                  {...linkStyle(isActive(`/retrieval/${currentProcessId}`))}
                >
                  <HStack spacing={3}>
                    <Icon as={FiSearch} fontSize="lg" />
                    <Text>检索进度</Text>
                  </HStack>
                </Link>
                
                <Link
                  as={RouterLink}
                  to={`/article/${currentProcessId}`}
                  {...linkStyle(isActive(`/article/${currentProcessId}`))}
                >
                  <HStack spacing={3}>
                    <Icon as={FiFileText} fontSize="lg" />
                    <Text>最终文章</Text>
                  </HStack>
                </Link>
              </VStack>
            </Box>
          </>
        )}
        
        <Box flex="1" />
        
        {/* 底部信息 */}
        <Box mt="auto" pt={4}>
          <Text fontSize="xs" color="gray.500" textAlign="center">
            © 2024 AI 编辑助手
          </Text>
        </Box>
      </VStack>
    </Box>
  );
};

export default Sidebar; 