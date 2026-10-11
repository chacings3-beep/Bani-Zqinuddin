import { Routes, Route } from "react-router-dom";
import Home from "@/pages/Home";
import Lookup from "@/pages/Lookup";
import Admin from "@/pages/Admin";

// One <Route> per page in src/pages; BrowserRouter already wraps this in main.tsx.
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/pesanan" element={<Lookup />} />
      <Route path="/admin" element={<Admin />} />
    </Routes>
  );
}
