import { NavLink } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/dashboard", label: "My squad" },
  { to: "/inspect", label: "Inspect other squads" },
  { to: "/tactics", label: "Tactics & formations" },
  { to: "/news", label: "News & trends" },
];

export default function Sidebar() {
  const scrollToChat = () => {
    document.getElementById("ask-the-analyst")?.scrollIntoView({ behavior: "smooth" });
    document.getElementById("chat-input")?.focus();
  };

  return (
    <nav className="w-56 shrink-0 border-r border-[#2a3344] bg-panel px-3 py-4 flex flex-col gap-1">
      {NAV_ITEMS.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) =>
            `rounded-card px-3 py-2 text-sm transition-colors ${
              isActive
                ? "bg-indigo/20 text-textPrimary border border-indigo/40"
                : "text-textSecondary hover:bg-cardHover hover:text-textPrimary"
            }`
          }
        >
          {item.label}
        </NavLink>
      ))}
      <button
        onClick={scrollToChat}
        className="text-left rounded-card px-3 py-2 text-sm text-textSecondary hover:bg-cardHover hover:text-textPrimary transition-colors"
      >
        Ask the analyst
      </button>
    </nav>
  );
}
