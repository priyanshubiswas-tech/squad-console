import { ReactNode } from "react";
import ChatPanel from "./ChatPanel";
import Header from "./Header";
import Sidebar from "./Sidebar";

export default function AppLayout({
  children,
  inspecting,
}: {
  children: ReactNode;
  inspecting?: string;
}) {
  return (
    <div className="h-screen flex flex-col">
      <Header inspecting={inspecting} />
      <div className="flex flex-1 min-h-0">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
        <ChatPanel />
      </div>
    </div>
  );
}
