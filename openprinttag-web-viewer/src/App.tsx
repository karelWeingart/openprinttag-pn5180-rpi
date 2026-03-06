import { Layout } from './features/Layout';
import { Navigation } from './features/Navigation';
import { MainTabs } from './features/MainTabs';
import { MqttMessageContext, LastMqttMessageContext } from './context/MqttMessageContext';
import { useApp } from './useApp';

const App: React.FC = () => {
  const { msgCount, lastMessage } = useApp();

  return (
      <Layout>
        <MqttMessageContext.Provider value={msgCount}>
          <LastMqttMessageContext.Provider value={lastMessage}>
            <Navigation appName="OpenPrintTag Viewer" version={process.env.REACT_APP_VERSION ?? "dev"} />
            <MainTabs />
          </LastMqttMessageContext.Provider>
        </MqttMessageContext.Provider>
      </Layout>
  );
}

export default App;
