import { Routes, Route, Link } from 'react-router-dom';
import { Box, Flex, Stack, Heading } from '@chakra-ui/react';
import HomePage from './pages/HomePage';
import InputPage from './pages/InputPage';
import OutlinePage from './pages/OutlinePage';
import RetrievalPage from './pages/RetrievalPage';
import ArticlePage from './pages/ArticlePage';

// 简单的侧边栏组件
const Sidebar = () => {
  return (
    <Box
      position="fixed"
      left={0}
      top={0}
      h="100vh"
      w="250px"
      bg="white"
      borderRightWidth="1px"
      borderRightColor="gray.200"
      p={4}
    >
      <Stack spacing={4}>
        <Heading size="md">AI 编辑助手</Heading>
        <Link to="/">主页</Link>
        <Link to="/input">新建文章</Link>
      </Stack>
    </Box>
  );
};

function App() {
  return (
    <Flex minH="100vh" bg="gray.50">
      <Sidebar />
      <Box flex="1" p={4} ml="250px">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/input" element={<InputPage />} />
          <Route path="/outline/:processId" element={<OutlinePage />} />
          <Route path="/retrieval/:processId" element={<RetrievalPage />} />
          <Route path="/article/:processId" element={<ArticlePage />} />
        </Routes>
      </Box>
    </Flex>
  );
}

export default App;
