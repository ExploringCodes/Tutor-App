import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { IntegrityScore, useIntegrityScore } from '../integrity_score/integrity_score';
import Stopwatch from '../Stopwatch/Stopwatch';
import './quiz.css';

const Quiz = ({ user, API_BASE_URL, subject, topic, subtopic, onCompleteQuiz }) => {
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [hardnessLevel, setHardnessLevel] = useState(5);
  const [questionsTried, setQuestionsTried] = useState(0);
  const [selectedOption, setSelectedOption] = useState('');
  const [isComplete, setIsComplete] = useState(false);
  const [completionMessage, setCompletionMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [score, setScore] = useState(0);
  const [isAnswerIncorrect, setIsAnswerIncorrect] = useState(false);
  const [isAnswerSubmitted, setIsAnswerSubmitted] = useState(false);
  const [timerReset, setTimerReset] = useState(0);
  const [showCongrats, setShowCongrats] = useState(false);
  const [isTimerPaused, setIsTimerPaused] = useState(false);
  const [attemptId, setAttemptId] = useState(null);

  // Integrity score hook
  const {
    questionStartTime,
    setQuestionStartTime,
    cheatScore,
    calculateCheatProbability,
    updateCheatScore,
    logResponseTime
  } = useIntegrityScore();

  // Start timing when a new question is loaded
  useEffect(() => {
    if (currentQuestion) {
      setQuestionStartTime(Date.now());
      setTimerReset((prev) => prev + 1);
      setIsTimerPaused(false);
    }
  }, [currentQuestion, setQuestionStartTime]);

  // Fetch the first quiz question on mount
  useEffect(() => {
    fetchQuizQuestion();
  }, []);

  const fetchQuizQuestion = async (submission = null) => {
    setIsLoading(true);
    try {
      const response = await axios.post(
        `${API_BASE_URL}/${subject}/${topic}/${subtopic}/quiz/`,
        submission,
        {
          headers: { 'user-id': user.user_id },
          withCredentials: true
        }
      );

      const { question, hardness_level, message, attempt_id, score, questions_tried } = response.data;
      if (question) {
        setCurrentQuestion(question);
        setHardnessLevel(hardness_level);
        setAttemptId(attempt_id);
        setSelectedOption('');
        setIsAnswerSubmitted(false);
        setIsAnswerIncorrect(false);
        setShowCongrats(false);
        setIsTimerPaused(false);
        // Update score and questions tried from response
        setScore(score || 0);
        setQuestionsTried(questions_tried || 0);
      } else if (message) {
        setIsComplete(true);
        setCompletionMessage(message);
        setAttemptId(attempt_id);
        // Update score and questions tried for completion
        setScore(score || 0);
        setQuestionsTried(questions_tried || 0);
      }
    } catch (error) {
      console.error('Error fetching quiz question:', error);
      alert('Error fetching quiz question. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnswerSelect = async (option) => {
    setSelectedOption(option);

    // Auto-submit the answer
    const responseTime = (Date.now() - questionStartTime) / 1000;
    const cheatProbability = calculateCheatProbability(responseTime);
    updateCheatScore(cheatProbability);
    const isCorrect = option === currentQuestion.correct_option;
    logResponseTime(responseTime, isCorrect, currentQuestion, hardnessLevel);

    setIsAnswerSubmitted(true);
    setIsAnswerIncorrect(!isCorrect);

    // Prepare submission
    const submission = {
      question_id: currentQuestion.id,
      is_correct: isCorrect,
      current_hardness_level: hardnessLevel,
      questions_tried: questionsTried + 1,
      attempt_id: attemptId
    };

    // Increment score and questionsTried
    //setQuestionsTried((prev) => prev + 1);
    if (isCorrect) {
     // setScore((prev) => prev + 1);
      setShowCongrats(true);
      setIsTimerPaused(true);
      setTimeout(async () => {
        await fetchQuizQuestion(submission);
      }, 1500);
    }
    // For incorrect answers, do not fetch new question immediately
    // Let handleNextQuestion trigger the fetch
  };

  const handleTimeExpired = () => {
    if (!isAnswerSubmitted) {
      const responseTime = (Date.now() - questionStartTime) / 1000;
      logResponseTime(responseTime, false, currentQuestion, hardnessLevel);
      setIsAnswerSubmitted(true);
      setIsAnswerIncorrect(true);

      const submission = {
        question_id: currentQuestion.id,
        is_correct: false,
        current_hardness_level: hardnessLevel,
        questions_tried: questionsTried + 1,
        attempt_id: attemptId
      };
      setQuestionsTried((prev) => prev + 1);
      fetchQuizQuestion(submission);
    }
  };

  const handleRetry = async () => {
    setSelectedOption('');
    setIsAnswerSubmitted(false);
    setIsAnswerIncorrect(false);
    setQuestionStartTime(Date.now());
    setTimerReset((prev) => prev + 1);
    setIsTimerPaused(false);
  };

  const handleNextQuestion = async () => {
    const submission = {
      question_id: currentQuestion.id,
      is_correct: false,
      current_hardness_level: hardnessLevel,
      questions_tried: questionsTried,
      attempt_id: attemptId
    };
    await fetchQuizQuestion(submission);
  };

  const handleCompleteQuiz = () => {
    onCompleteQuiz();
  };

  const integrityScore = 100 - cheatScore;

  if (isComplete) {
    return (
      <div className="practice-quiz-container">
        <h2>Quiz Session Complete</h2>
        <p>{completionMessage}</p>
        <p>Score: {score} / {questionsTried}</p>
        <p>Total Questions Tried: {questionsTried}</p>
        <p>Final Difficulty Level: {hardnessLevel}</p>
        <IntegrityScore integrityScore={integrityScore} cheatScore={cheatScore} />
        <button onClick={handleCompleteQuiz} className="primary-button">
          Return to Dashboard
        </button>
      </div>
    );
  }

  if (isLoading || !currentQuestion) {
    return (
      <div className="practice-quiz-container">
        <div className="loading">
          <div className="loading-spinner"></div>
          <p>Loading quiz question...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="practice-quiz-container">
      <h2>Quiz: {subject} - {topic} - {subtopic}</h2>
      <div className="quiz-header">
        <p>Question {questionsTried + 1} | Difficulty Level: {hardnessLevel}</p>
        <Stopwatch reset={timerReset} onTimeExpired={handleTimeExpired} pause={isTimerPaused} />
        <p>Score: {score} / {questionsTried}</p>
      </div>
      <div className="integrity-score">
        <span>Integrity Score</span>
        <span>{integrityScore}%</span>
      </div>
      <IntegrityScore integrityScore={integrityScore} cheatScore={cheatScore} />
      <div className="question-container">
        <h4>{currentQuestion.question}</h4>
        <div className="options">
          {['a', 'b', 'c', 'd'].map((option) => (
            <div key={option} className="option">
              <input
                type="radio"
                id={`q-${currentQuestion.id}-${option}`}
                name={`question-${currentQuestion.id}`}
                value={option}
                checked={selectedOption === option}
                onChange={() => handleAnswerSelect(option)}
                disabled={isAnswerSubmitted}
              />
              <label htmlFor={`q-${currentQuestion.id}-${option}`}>
                {option.toUpperCase()}: {currentQuestion[`option_${option}`]}
              </label>
            </div>
          ))}
        </div>
      </div>
      {showCongrats && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="feedback correct">
              <h3>Correct!</h3>
              <p>Well done! You selected the right answer.</p>
              <p>Great speed!</p>
              <p>Moving to a more challenging question...</p>
            </div>
          </div>
        </div>
      )}
      {isAnswerSubmitted && isAnswerIncorrect && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="feedback incorrect">
              <h3>Incorrect</h3>
              <p>Your answer was incorrect.</p>
              <p>
                <strong>Correct Answer:</strong> {currentQuestion.correct_option.toUpperCase()}: {currentQuestion[`option_${currentQuestion.correct_option}`]}
              </p>
              <p className="explanation">
                <strong>Explanation:</strong> {currentQuestion.explanation}
              </p>
            </div>
            <div className="action-buttons">
              <button onClick={handleNextQuestion} className="next-button">
                Next Question
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Quiz;