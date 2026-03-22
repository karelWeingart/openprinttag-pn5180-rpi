import { useState } from "react";
import { TabsRow } from "../../components/TabsRow";
import { HistoryTable } from "../HistoryTable/HistoryTable";
import { WriteTag } from "../WriteTag";
import { Printers } from "../Printers/Printers";

const TABS = ["History", "Write Tag", "Printers"];

export function MainTabs() {
  const [activeTab, setActiveTab] = useState(TABS[0]);

  return (
    <>
      <TabsRow tabs={TABS} activeTab={activeTab} onTabSelect={setActiveTab} />
      <div className="tab-content p-3">
        {activeTab === "History" && <HistoryTable />}
        {activeTab === "Write Tag" && <WriteTag />}
        {activeTab === "Printers" && <Printers />}
      </div>
    </>
  );
}