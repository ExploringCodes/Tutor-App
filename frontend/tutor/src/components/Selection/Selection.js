import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Selection.css';

const Selection = ({ user, API_BASE_URL, onSelectionSubmit,logInteraction }) => {
  const [subjects, setSubjects] = useState([]);
  const [topics, setTopics] = useState([]);
  const [subtopics, setSubtopics] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState('');
  const [selectedTopic, setSelectedTopic] = useState('');
  const [selectedSubtopic, setSelectedSubtopic] = useState('');


  // Fetch subjects when the component mounts
  useEffect(() => {
    const fetchSubjects = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/subjects/`, {
          headers: { 'user-id': user.user_id },
          withCredentials: true
        });
        setSubjects(response.data);
      } catch (error) {
        console.error('Error fetching subjects:', error);
        alert('Error fetching subjects. Please try again.');
      }
    };
    fetchSubjects();
  }, [API_BASE_URL, user.user_id]);

  // Fetch topics when a subject is selected
  useEffect(() => {
    if (selectedSubject) {
      const fetchTopics = async () => {
        try {
          const response = await axios.get(`${API_BASE_URL}/${selectedSubject}/topics/`, {
            headers: { 'user-id': user.user_id },
            withCredentials: true
          });
          setTopics(response.data);
        } catch (error) {
          console.error('Error fetching topics:', error);
          alert('Error fetching topics. Please try again.');
        }
      };
      fetchTopics();
    }
  }, [selectedSubject, API_BASE_URL, user.user_id]);

  // Fetch subtopics when a topic is selected
  useEffect(() => {
    if (selectedTopic && selectedSubject) {
      const fetchSubtopics = async () => {
        try {
          const response = await axios.get(`${API_BASE_URL}/${selectedSubject}/${selectedTopic}/subtopics/`, {
            headers: { 'user-id': user.user_id },
            withCredentials: true
          });
          setSubtopics(response.data);
        } catch (error) {
          console.error('Error fetching subtopics:', error);
          alert('Error fetching subtopics. Please try again.');
        }
      };
      fetchSubtopics();
    }
  }, [selectedTopic, selectedSubject, API_BASE_URL, user.user_id]);

  // Handle form submission for confirmation
  const handleConfirmSelection = async (e) => {
    e.preventDefault();
    if (!selectedSubject || !selectedTopic || !selectedSubtopic) {
      alert('Please select a subject, topic, and subtopic');
      return;
    }

    try {
      // Make the selection API call
      await axios.post(
        `${API_BASE_URL}/select/`,
        { subject: selectedSubject, topic: selectedTopic, subtopic: selectedSubtopic },
        {
          headers: { 'user-id': user.user_id },
          withCredentials: true
        }
      );
      logInteraction(user.user_id, 'button_click', 'Clicked Confirm Selection');
      // Notify App.js of the confirmed selection
      onSelectionSubmit({ selectedSubject, selectedTopic, selectedSubtopic });
      alert('Selection confirmed! Use the navigation buttons to proceed.');
    } catch (error) {
      console.error('Error during selection:', error);
      alert('Error during selection. Please try again.');
    }
  };

  return (
    <div className="selection-component-container">
      <h2>Select Subject, Topic, and Subtopic</h2>
      <form onSubmit={handleConfirmSelection}>
        <div className="selection-group-component">
          <label>Subject:</label>
          <select
            value={selectedSubject}
            onChange={(e) => {
              setSelectedSubject(e.target.value);
              setSelectedTopic('');
              setSelectedSubtopic('');
              logInteraction(user.user_id, 'dropdown_select', `Selected subject: ${e.target.value}`);
            }}
            required
          >
            <option value="">Select a Subject</option>
            {subjects.map((subject) => (
              <option key={subject.id} value={subject.name}>
                {subject.name}
              </option>
            ))}
          </select>
        </div>

        <div className="selection-group-component">
          <label>Topic:</label>
          <select
            value={selectedTopic}
            onChange={(e) => {
              setSelectedTopic(e.target.value);
              setSelectedSubtopic('');
              logInteraction(user.user_id, 'dropdown_select', `Selected topic: ${e.target.value}`);
            }}
            disabled={!selectedSubject}
            required
          >
            <option value="">Select a Topic</option>
            {topics.map((topic) => (
              <option key={topic.id} value={topic.name}>
                {topic.name}
              </option>
            ))}
          </select>
        </div>

        <div className="selection-group-component">
          <label>Subtopic:</label>
          <select
            value={selectedSubtopic}
            onChange={(e) =>{ setSelectedSubtopic(e.target.value)
              logInteraction(user.user_id, 'dropdown_select', `Selected subtopic: ${e.target.value}`);}
            }
            disabled={!selectedTopic}
            required

          >
            <option value="">Select a Subtopic</option>
            {subtopics.map((subtopic) => (
              <option key={subtopic.id} value={subtopic.name}>
                {subtopic.name}
              </option>
            ))}
          </select>
        </div>

        <button
          type="submit"
          disabled={!selectedSubject || !selectedTopic || !selectedSubtopic}
        >
          Confirm Selection
        </button>
      </form>
    </div>
  );
};

export default Selection;