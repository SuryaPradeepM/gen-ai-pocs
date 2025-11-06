import './App.css';
import { Route, Routes } from 'react-router-dom';
import Header from './Components/Header/Header';
import MeetingSummary from './Pages/MeetingSummary/MeetingSummary';
import Dashboard from './Pages/Dashboard/Dashboard';
import Summary from './Pages/Summary/Summary';
import PPTUpload from './Pages/VirtualPresenter/FileUpload/fileUpload'
import LogoGenerator from './Pages/LogoGenerator/LogoGenerator';
import RAGChatbot from './Pages/RAGChatbot/RAGChatbot';
import HRPoliciesChatbot from './Pages/HRPoliciesChatbot/HRPoliciesChatbot';

function App() {
  return (
    <div className="App">
      <Header />
      <Routes>
        <Route path='/' element={<Dashboard />} />
        <Route path='/meeting_summary' element={<MeetingSummary />} />
        <Route path='/summary' element={<Summary />} />
        <Route path='/virtual_presenter' element={<PPTUpload />} />
        <Route path="/logo_generator" element={<LogoGenerator />} />
        <Route path="/rag-chatbot" element={<RAGChatbot />} />
        <Route path="/hr-policies-chatbot" element={<HRPoliciesChatbot />} />
      </Routes>
    </div>
  );
}

export default App;