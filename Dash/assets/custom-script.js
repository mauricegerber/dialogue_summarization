import React, { Component } from 'react';
export default class HighlightText extends Component {
  constructor(props) {
    super(props);
    this.state = { searchText: '' };
    this.search = this.search.bind(this);
  }
  search(event) {
    this.setState({ searchText: event.target.value });
  }
  _getText(text, searchText) {
    return searchText ? this._getTextWithHighlights(text, searchText) : text;
  }
  _getTextWithHighlights(text, searchText) {
    const regex = new RegExp(searchText, 'gi');
    const newText = text.replace(regex, `<mark class="highlight">$&</mark>`);
    return <span dangerouslySetInnerHTML={{ __html: newText }} />;
  }
  render() {
    const { cite, text } = this.props;
    const { searchText } = this.state;
    const textToShow = this._getText(text, searchText);
    return (
      <div className="container">
        <div className="search-container">
          <label htmlFor="search">Search within quoted text</label>
          <input
            id="search"
            placeholder="Type `web` for example"
            type="search"
            autoComplete="off"
            onChange={this.search}
            value={searchText}
          />
        </div>
        <blockquote cite={cite}>{textToShow}</blockquote>
      </div>
    );
  }
}