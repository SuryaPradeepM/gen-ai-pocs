import { Component } from "react";
import GenAIContext from "./genai-context";
let self;
class GlobalState extends Component {
  constructor(props) {
    super(props);
    self = this;
    this.state = {
      userDetails: null,
      heading: null,
      workSpaceDetails: null,
      createLabel: false,
      selectedDataSourceId: null,
      docIndexMap: {},
      sectionLabels: [],
      isUploadTemplate: false,
      registryScreenNumber: null,
      headerAvailable: null,
      selectedChunkValues: [],
      selectedBotOnHome: "PIN",
      workspaceScreenNumber: 0,
      workspaceId: null,
      templateList: [],
    };
  }

  componentDidMount = () => {};

  setDocIndexMap = (docIndMap) => {
    self.setState({ docIndexMap: docIndMap });
  };

  setHeading = (type) => {
    self.setState({ heading: type });
  };

  setWorkSpaceDetails = (data) => {
    self.setState({ workSpaceDetails: data });
  };

  setCreateLabel = (createStatus) => {
    self.setState({ createLabel: createStatus });
  };
  setSelectedDataSourceId = (id) => {
    self.setState({ selectedDataSourceId: id });
  };

  setSectionLabels = (labels) => {
    self.setState({ sectionLabels: labels });
  };
  setIsUploadTemplate = (status) => {
    self.setState({ isUploadTemplate: status });
  };

  setHeaderAvailable = (val) => {
    self.setState({ headerAvailable: val });
  };

  setRegistryScreenNumber = (val) => {
    self.setState({ registryScreenNumber: val });
  };
  setSelectedChunks = (selectedVals) => {
    self.setState({ selectedChunkValues: selectedVals });
  };

  setSelectedBotOnHome = (botName) => {
    self.setState({ selectedBotOnHome: botName });
  };

  setWorkspaceScreenNumber = (val) => {
    self.setState({ workspaceScreenNumber: val });
  };

  setWorkspaceId = (id) => {
    self.setState({ workspaceId: id });
  };

  setTemplateList = (value) => {
    self.setState((prevState) => ({
      templateList: [...prevState.templateList, value],
    }));
  };

  render() {
    const { children } = this.props;
    const {
      templateList,
      userDetails,
      selectedBotOnHome,
      workspaceScreenNumber,
      workspaceId,
      heading,
      workSpaceDetails,
      registryScreenNumber,
      createLabel,
      selectedDataSourceId,
      docIndexMap,
      sectionLabels,
      isUploadTemplate,
      headerAvailable,
      selectedChunkValues,
    } = this.state;
    const {
      setTemplateList,
      setHeading,
      setSelectedBotOnHome,
      setWorkspaceScreenNumber,
      setWorkspaceId,
      setWorkSpaceDetails,
      setCreateLabel,
      setSelectedDataSourceId,
      setDocIndexMap,
      setSectionLabels,
      setIsUploadTemplate,
      setRegistryScreenNumber,
      setHeaderAvailable,
      setSelectedChunks,
    } = this;
    return (
      <GenAIContext.Provider
        value={{
          userDetails,
          workSpaceDetails,
          createLabel,
          selectedDataSourceId,
          workspaceId,
          docIndexMap,
          sectionLabels,
          isUploadTemplate,
          headerAvailable,
          selectedChunkValues,
          selectedBotOnHome,
          workspaceScreenNumber,
          templateList,
          setTemplateList,
          setDocIndexMap,
          setHeading,
          setWorkSpaceDetails,
          setCreateLabel,
          setSelectedDataSourceId,
          setSectionLabels,
          setIsUploadTemplate,
          setWorkspaceId,
          registryScreenNumber,
          setRegistryScreenNumber,
          setHeaderAvailable,
          setSelectedBotOnHome,
          setSelectedChunks,
          setWorkspaceScreenNumber,
          heading,
        }}
      >
        {children}
      </GenAIContext.Provider>
    );
  }
}

export default GlobalState;
