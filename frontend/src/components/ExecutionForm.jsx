import React, { useState } from 'react';
import { Play } from 'lucide-react';

const DEFAULT_PROMPT = "Extract the user's name and age from the text.";
const DEFAULT_CONTEXT = "John is 30 years old and lives in New York.";
const DEFAULT_SCHEMA = "{\n  \"type\": \"object\",\n  \"properties\": {\n    \"name\": {\"type\": \"string\"},\n    \"age\": {\"type\": \"integer\"}\n  },\n  \"required\": [\"name\", \"age\"]\n}";

const SCHEMA_PRESETS = {
  "Name + Age": { type: "object", properties: { name: {type:"string"}, age: {type:"integer"} }, required: ["name","age"] },
  "Name + Age + City": { type: "object", properties: { name: {type:"string"}, age: {type:"integer"}, city: {type:"string"} }, required: ["name","age","city"] },
  "Product Name + Price": { type: "object", properties: { name: {type:"string"}, price: {type:"number"} }, required: ["name","price"] },
};

function SchemaPresetSelect({ onSelect }) {
  return (
    <select onChange={(e) => {
      const preset = SCHEMA_PRESETS[e.target.value];
      if (preset) onSelect(JSON.stringify(preset, null, 2));
    }} style={{ marginLeft: '1rem', padding: '0.2rem 0.5rem', borderRadius: '4px', border: '1px solid var(--border-color)', background: 'rgba(255,255,255,0.05)', color: 'white' }}>
      <option value="">Custom (type below)</option>
      {Object.keys(SCHEMA_PRESETS).map(name => (
        <option key={name} value={name}>{name}</option>
      ))}
    </select>
  );
}

export default function ExecutionForm({ onSubmit, loading }) {
  const [prompt, setPrompt] = useState(DEFAULT_PROMPT);
  const [context, setContext] = useState(DEFAULT_CONTEXT);
  const [schema, setSchema] = useState(DEFAULT_SCHEMA);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ prompt, expected_schema: schema, context });
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-group">
        <label>Prompt</label>
        <textarea 
          className="form-control" 
          value={prompt} 
          onChange={e => setPrompt(e.target.value)}
          required
        />
      </div>
      <div className="form-group">
        <label>Context (for Grounding/Hallucination Check)</label>
        <textarea 
          className="form-control" 
          value={context} 
          onChange={e => setContext(e.target.value)}
        />
      </div>
      <div className="form-group">
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '0.5rem' }}>
          <label style={{ margin: 0 }}>Expected JSON Schema</label>
          <SchemaPresetSelect onSelect={setSchema} />
        </div>
        <textarea 
          className="form-control" 
          value={schema} 
          onChange={e => setSchema(e.target.value)}
          style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}
          required
        />
      </div>
      <button type="submit" className="btn btn-primary" disabled={loading} style={{ width: '100%' }}>
        {loading ? <div className="spinner"></div> : <Play size={18} style={{ marginRight: '8px' }} />}
        {loading ? 'Executing Pipeline...' : 'Execute Request'}
      </button>
    </form>
  );
}
