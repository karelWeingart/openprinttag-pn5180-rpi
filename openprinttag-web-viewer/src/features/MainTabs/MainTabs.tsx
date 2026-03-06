import { useState } from "react";
import { TabsRow } from "../../components/TabsRow";
import { HistoryTable } from "../HistoryTable/HistoryTable";
import { WriteTag } from "../WriteTag";

const TABS = ["History", "Write Tag"];

export function MainTabs() {
  const [activeTab, setActiveTab] = useState(TABS[0]);

  return (
    <>
      <TabsRow tabs={TABS} activeTab={activeTab} onTabSelect={setActiveTab} />
      <div className="tab-content p-3">
        {activeTab === "History" && <HistoryTable />}
        {activeTab === "Write Tag" && <WriteTag />}
      </div>
    </>
  );
}