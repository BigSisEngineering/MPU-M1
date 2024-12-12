import React from "react";
import { ContentProvider } from "./Middleware/get-api.js";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./Pages/Layout";
import Operation from "./Pages/Operation";
import Display from "./Pages/Display";
import Debugging from "./Pages/Debugging";

export default function Webapp() {
  return (
    <>
      <BrowserRouter>
        <ContentProvider>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<Operation />} />
              <Route path="Display" element={<Display />} />
              <Route path="Debugging" element={<Debugging />} />
            </Route>
          </Routes>
        </ContentProvider>
      </BrowserRouter>
    </>
  );
}
