import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [error, setError] = useState(null);
  const [isSignUp, setIsSignUp] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // CONFIGURE BACKEND URL HERE:
  // Use your current LAN IP so that your phone can reach the backend
  //const BACKEND_BASE = 'http://10.106.91.44:8000'; // <-- CHANGE THIS as needed
  const BACKEND_BASE = 'http://127.0.0.1:8000';


  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const url = isSignUp
        ? `${BACKEND_BASE}/api/signup/`
        : `${BACKEND_BASE}/api/login/`;
      const payload = isSignUp
        ? { username, password, email }
        : { username, password };
      console.log('Posting to:', url, 'Payload:', payload);

      const response = await axios.post(url, payload);
      const { access, refresh, user } = response.data;
      console.log('Login/signup response:', response.data);

      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      localStorage.setItem('user', JSON.stringify(user));
      setLoading(false);

      navigate('/scan');
      console.log('Navigated to /scan!');
    } catch (error) {
      setLoading(false);
      console.error('Login/signup error:', error);
      if (error.response) {
        console.error('Error Response:', error.response);
        setError(
          error.response.data?.error ||
          JSON.stringify(error.response.data) ||
          'An error occurred'
        );
      } else {
        setError(error.message || 'An error occurred');
      }
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '400px', margin: '0 auto', textAlign: 'center' }}>
      <h1>TasinAI</h1>
      <h2>{isSignUp ? 'Sign Up' : 'Login'}</h2>
      {/* The following section is for debugging and can be commented out
        when you are no longer troubleshooting network connection issues.
        <div style={{ background: "#f9f9f9", fontSize: 12, padding: 6, marginBottom: 6, color: "#555" }}>
          <span>Current window.location: <code>{window.location.href}</code><br /></span>
          <span>Backend base URL: <code>{BACKEND_BASE}</code></span>
        </div>
      */}
      {error && <p style={{ color: 'red', fontWeight: "bold" }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Username"
          value={username}
          autoComplete="username"
          onChange={e => setUsername(e.target.value)}
          style={{ width: '100%', padding: '8px', margin: '10px 0' }}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          autoComplete="current-password"
          onChange={e => setPassword(e.target.value)}
          style={{ width: '100%', padding: '8px', margin: '10px 0' }}
          required
        />
        {isSignUp && (
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            style={{ width: '100%', padding: '8px', margin: '10px 0' }}
            required
          />
        )}
        <button
          type="submit"
          disabled={loading}
          style={{ width: '100%', padding: '10px', background: '#1e90ff', color: 'white', border: 'none' }}
        >
          {loading ? 'Please wait...' : (isSignUp ? 'Sign Up' : 'Login')}
        </button>
      </form>

      <p>
        {isSignUp ? 'Already have an account? ' : "Don't have an account? "}
        <button
          onClick={() => setIsSignUp(!isSignUp)}
          style={{ background: 'none', border: 'none', color: '#1e90ff', cursor: 'pointer' }}
        >
          {isSignUp ? 'Login' : 'Sign Up'}
        </button>
      </p>

      {/* --- Debug/testing: Force navigate to scan page --- */}
      <div style={{ marginTop: 40 }}>
        <button
          onClick={() => {
            console.log('TEMP: Direct navigation to /scan triggered!');
            navigate('/scan');
          }}
          style={{ background: '#f6c343', border: 'none', color: '#333', padding: '10px 24px', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
        >
          TEMP: Go to Scan Page
        </button>
      </div>
    </div>
  );
}

export default Login;
