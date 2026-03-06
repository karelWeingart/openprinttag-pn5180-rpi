import { Tab } from "./Tab";

interface TabsRowProps {
  tabs: string[];
  activeTab: string;
  onTabSelect: (tab: string) => void;
}

export function TabsRow({ tabs, activeTab, onTabSelect }: TabsRowProps) {
  return (
    <ul className="nav nav-tabs pe-3 ps-3">
      {tabs.map((tab) => (
        <Tab
          key={tab}
          title={tab}
          isActive={tab === activeTab}
          onClick={() => onTabSelect(tab)}
        />
      ))}
    </ul>
  );
}