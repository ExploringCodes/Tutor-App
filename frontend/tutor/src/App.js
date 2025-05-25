import React, { useState, useEffect } from 'react';
import Quiz1 from './components/Quiz1/quiz1';
import Selection from './components/Selection/Selection';
import Explains from './components/Explains/Explains';
import PracticeQuiz from './components/Practise/Practise';
import Quiz from './components/Quiz/quiz';
import axios from 'axios';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [quizStage, setQuizStage] = useState('quiz1');
  const [selectedValues, setSelectedValues] = useState({
    selectedSubject: '',
    selectedTopic: '',
    selectedSubtopic: ''
  });
  const API_BASE_URL = 'http://localhost:8000';
  const logInteraction = async (userId, type, details) => {
    if (!userId || typeof userId !== 'number') {
        console.error('Invalid userId for logging interaction:', userId);
        return;
    }
    try {
        await axios.post(`${API_BASE_URL}/interactions`, {
            user_id: userId,
            interaction_type: type,
            details: details
        },{
            withCredentials: true
        });
        console.log('Interaction logged:', type, details);
    } catch (error) {
        console.error('Error logging interaction:', error);
    }
};

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/user`, {
      credentials: 'include'
    })
      .then(response => response.json())
      .then(data => {
        setUser({
          email: data.user.email,
          user_id: data.user.id,
          picture: data.user.picture,
          name: data.user.name
        });
        if (data.user) {
          console.log('User Email:', data.user.email);
          console.log('User ID:', data.user.id);
          console.log('user name', data.user.name);
        }
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching user:', error);
        setLoading(false);
      });
  }, []);

  const handleLogin = () => {
    window.location.href = `${API_BASE_URL}/login`;
  };

  const handleLogout = () => {
    fetch(`${API_BASE_URL}/logout`, {
      credentials: 'include'
    })
      .then(() => {
        setUser(null);
        setQuizStage('quiz1');
        setSelectedValues({ selectedSubject: '', selectedTopic: '', selectedSubtopic: '' });
      })
      .catch(error => console.error('Error logging out:', error));
  };

  const onQuiz1Complete = () => {
    setQuizStage('selection');
  };

  const onSelectionSubmit = (values) => {
    setSelectedValues(values);
    // Stay in selection stage, do not auto-advance to explains
  };

  const onProceedToPractice = () => {
    setQuizStage('practice');
  };

  const onCompletePractice = () => {
    setQuizStage('quiz');
  };

  const onCompleteQuiz = () => {
    setSelectedValues({ selectedSubject: '', selectedTopic: '', selectedSubtopic: '' });
    setQuizStage('selection');
  };

  const areSelectionsComplete = () => {
    return (
      selectedValues.selectedSubject &&
      selectedValues.selectedTopic &&
      selectedValues.selectedSubtopic
    );
  };

  const handleStageChange = (stage) => {
    if (['explains', 'practice', 'quiz'].includes(stage) && !areSelectionsComplete()) {
      setQuizStage('selection');
    } else {
      setQuizStage(stage);
    }
  };

  const renderCurrentStage = () => {
    if (!user) {
      return (
        <div className="text-center">
          <h2 className="text-2xl mb-4">Please Log In</h2>
          <button
            onClick={handleLogin}
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          >
            Login with Google
          </button>
        </div>
      );
    }

    switch (quizStage) {
      case 'quiz1':
        return <Quiz1 user={user} API_BASE_URL={API_BASE_URL} onCompleteQuiz={onQuiz1Complete} />;
      case 'selection':
        return (
          <Selection user={user} API_BASE_URL={API_BASE_URL} onSelectionSubmit={onSelectionSubmit} logInteraction={logInteraction} />
        );
      case 'explains':
        return (
          <Explains
            selectedSubject={selectedValues.selectedSubject}
            selectedTopic={selectedValues.selectedTopic}
            selectedSubtopic={selectedValues.selectedSubtopic}
            user={user}
            API_BASE_URL={API_BASE_URL}
            onProceedToPractice={onProceedToPractice}
          />
        );
      case 'practice':
        return (
          <PracticeQuiz
            user={user}
            API_BASE_URL={API_BASE_URL}
            subject={selectedValues.selectedSubject}
            topic={selectedValues.selectedTopic}
            subtopic={selectedValues.selectedSubtopic}
            onCompletePractice={onCompletePractice}
          />
        );
      case 'quiz':
        return (
          <Quiz
            user={user}
            API_BASE_URL={API_BASE_URL}
            subject={selectedValues.selectedSubject}
            topic={selectedValues.selectedTopic}
            subtopic={selectedValues.selectedSubtopic}
            onCompleteQuiz={onCompleteQuiz}
          />
        );
      default:
        return <Quiz1 user={user} API_BASE_URL={API_BASE_URL} onCompleteQuiz={onQuiz1Complete} />;
    }
  };

  const renderNavigationButtons = () => {
    if (!user) return null;

    return (
      <div className="navigation-buttons flex justify-center gap-4 mt-4">
        <button
          onClick={() => handleStageChange('quiz1')}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Quiz 1
        </button>
        <button
          onClick={() => handleStageChange('selection')}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Selection
        </button>
        <button
          onClick={() => handleStageChange('explains')}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Explains
        </button>
        <button
          onClick={() => handleStageChange('practice')}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Practice
        </button>
        <button
          onClick={() => handleStageChange('quiz')}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Quiz
        </button>
      </div>
    );
  };

  if (loading) {
    return <div className="text-center mt-10">Loading...</div>;
  }

  return (
    <div className="App min-h-screen flex flex-col">
      <header className="App-header bg-gray-800 text-white p-4 text-center">
        <h1 className="text-3xl">AI Tutor Quiz Application</h1>
        {user && (
          <div className="user-info flex items-center justify-center gap-4 mt-2">
            {user.picture && (
              <img src={user.picture} alt="Profile" className="w-10 h-10 rounded-full" />
            )}
            <span>Welcome, {user.name}</span>
            <button
              onClick={handleLogout}
              className="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-3 rounded"
            >
              Logout
            </button>
          </div>
        )}
      </header>
      <main className="flex-grow p-4">
        {renderCurrentStage()}
        {renderNavigationButtons()}
      </main>
      <footer className="bg-gray-200 p-2 text-center">
        <p>Status: {user ? `Logged in as ${user.email}` : 'Not logged in'}</p>
      </footer>
    </div>
  );
}

export default App;