import { Outlet } from "react-router";

import Navigation from "./components/Navbar";

function App() {
  return (
    <div>
      <Navigation />
      <Outlet />
    </div>
  );
}

export default App;
