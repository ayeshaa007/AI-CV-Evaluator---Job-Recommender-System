import { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);         // null = not logged in
  const [history, setHistory] = useState([]);     // saved analyses

  // Load from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem("resumeai_user");
    if (saved) {
      const u = JSON.parse(saved);
      setUser(u);
      const h = JSON.parse(localStorage.getItem(`resumeai_history_${u.email}`) || "[]");
      setHistory(h);
    }
  }, []);

  const login = (email, password) => {
    // Simple client-side auth (no real backend needed for demo)
    const users = JSON.parse(localStorage.getItem("resumeai_users") || "[]");
    const found = users.find(u => u.email === email && u.password === password);
    if (!found) throw new Error("Invalid email or password");
    const { password: _, ...safeUser } = found;
    setUser(safeUser);
    localStorage.setItem("resumeai_user", JSON.stringify(safeUser));
    const h = JSON.parse(localStorage.getItem(`resumeai_history_${email}`) || "[]");
    setHistory(h);
    return safeUser;
  };

  const signup = (name, email, password) => {
    const users = JSON.parse(localStorage.getItem("resumeai_users") || "[]");
    if (users.find(u => u.email === email)) throw new Error("Email already registered");
    const newUser = {
      name,
      email,
      password,
      initials: name.split(" ").map(n => n[0]).join("").toUpperCase().slice(0, 2),
      joinedAt: new Date().toISOString(),
    };
    users.push(newUser);
    localStorage.setItem("resumeai_users", JSON.stringify(users));
    const { password: _, ...safeUser } = newUser;
    setUser(safeUser);
    localStorage.setItem("resumeai_user", JSON.stringify(safeUser));
    setHistory([]);
    return safeUser;
  };

  const logout = () => {
    setUser(null);
    setHistory([]);
    localStorage.removeItem("resumeai_user");
  };

  const saveAnalysis = (result, role, fileName) => {
    if (!user) return; // guests don't save
    const entry = {
      id:       Date.now(),
      date:     new Date().toISOString(),
      role,
      fileName,
      score:    result.overallScore,
      result,
    };
    const updated = [entry, ...history].slice(0, 20); // keep last 20
    setHistory(updated);
    localStorage.setItem(`resumeai_history_${user.email}`, JSON.stringify(updated));
  };

  const deleteAnalysis = (id) => {
    const updated = history.filter(h => h.id !== id);
    setHistory(updated);
    if (user) {
      localStorage.setItem(`resumeai_history_${user.email}`, JSON.stringify(updated));
    }
  };

  return (
    <AuthContext.Provider value={{ user, history, login, signup, logout, saveAnalysis, deleteAnalysis }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
