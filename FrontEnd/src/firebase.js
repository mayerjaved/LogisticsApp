import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getDatabase } from 'firebase/database';

const firebaseConfig = {
  apiKey: "AIzaSyCw7EegvMBXwbuMr5s69f-uza7zYGLNkYw",
  authDomain: "tasin-logistics-ai.firebaseapp.com",
  databaseURL: "https://tasin-logistics-ai-default-rtdb.firebaseio.com",
  projectId: "tasin-logistics-ai",
  storageBucket: "tasin-logistics-ai.firebasestorage.app",
  messagingSenderId: "717907256241",
  appId: "1:717907256241:web:854a53a8d978655e2b5390",
  measurementId: "G-BT0P67ELH9"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const database = getDatabase(app);