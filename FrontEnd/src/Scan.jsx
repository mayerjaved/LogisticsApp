import { useState } from 'react';
import BarcodeScanner from 'react-qr-barcode-scanner';
import axios from 'axios';

// Assume this is your backend base URL, matching your Django server
const BACKEND_BASE = 'http://127.0.0.1:8000';

// A component to display the details of a single scanned item
const BarcodeDetailsWidget = ({ item, onRemove }) => {
  const [isMaximized, setIsMaximized] = useState(true);

  // SVG for the arrow icon
  const ArrowIcon = ({ direction }) => (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="#1e90ff"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      style={{
        transition: 'transform 0.3s ease',
        transform: direction === 'down' ? 'rotate(0deg)' : 'rotate(-90deg)',
      }}
    >
      <polyline points="6 9 12 15 18 9" />
    </svg>
  );

  // SVG for the close icon
  const CloseIcon = () => (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="#8B0000"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      style={{ cursor: 'pointer', transition: 'transform 0.2s ease', ':hover': { transform: 'scale(1.1)' } }}
    >
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );

  return (
    <div style={{
      position: 'relative',
      background: 'white',
      borderRadius: 12,
      padding: '16px 20px',
      marginBottom: 16,
      boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
      width: '100%',
      maxWidth: 360,
      boxSizing: 'border-box',
      transition: 'all 0.3s ease',
      paddingBottom: isMaximized ? '16px' : '4px',
    }}>
      {/* Removal Button */}
      <button
        onClick={(e) => {
          e.stopPropagation(); // Prevents the widget from maximizing/minimizing
          onRemove(item.barcode);
        }}
        style={{
          position: 'absolute',
          top: 14,
          right: 40,
          background: 'transparent',
          border: 'none',
          padding: 0,
          cursor: 'pointer',
        }}
      >
        <CloseIcon />
      </button>

      {/* Main widget content, clickable to toggle state */}
      <div
        onClick={() => setIsMaximized(!isMaximized)}
        style={{
          cursor: 'pointer',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ margin: '0', color: '#1e90ff', fontWeight: 'bold' }}>{item.client_name}</h3>
          <ArrowIcon direction={isMaximized ? 'down' : 'right'} />
        </div>
        {isMaximized && (
          <div style={{ paddingTop: '8px' }}>
            {item.delivery_index !== undefined && (
              <p style={{ margin: '0 0 4px 0', fontSize: 14 }}>
                <strong>Route Index:</strong> {item.delivery_index + 1}
              </p>
            )}
            <p style={{ margin: '0 0 4px 0', fontSize: 14 }}>
              <strong>Barcode:</strong> {item.barcode}
            </p>
            <p style={{ margin: '0 0 4px 0', fontSize: 14 }}>
              <strong>Item:</strong> {item.item_name}
            </p>
            <p style={{ margin: '0 0 4px 0', fontSize: 14 }}>
              <strong>Address:</strong> {item.delivery_address}
            </p>
            <p style={{ margin: '0 0 0 0', fontSize: 14 }}>
              <strong>Due:</strong> {item.due_time || 'Not specified'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default function Scan() {
  const [activeTab, setActiveTab] = useState('deliver');
  const [scanResult, setScanResult] = useState('No result');
  const [typedBarcode, setTypedBarcode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [scannedItems, setScannedItems] = useState([]);
  const [isScannerActive, setIsScannerActive] = useState(false);
  const [isManualInputActive, setIsManualInputActive] = useState(false);

  // Check if all scanned items belong to the same route to enable optimization
  const firstItemRoute = scannedItems.length > 0 ? scannedItems[0].route_id : null;
  const isSameRoute = scannedItems.every(item => item.route_id === firstItemRoute);
  const isOptimizeButtonEnabled = scannedItems.length >= 2 && isSameRoute;

  const handleLookup = async (barcode) => {
    if (!barcode || scannedItems.some(item => item.barcode === barcode)) {
      setTypedBarcode('');
      return;
    }

    setLoading(true);
    setError(null);
    setScanResult(barcode);

    try {
      const url = `${BACKEND_BASE}/api/barcode-details/${barcode}/`;
      const response = await axios.get(url);
      const itemData = response.data;
      setScannedItems(prevItems => [itemData, ...prevItems]);
      setTypedBarcode('');
      setIsScannerActive(false);
      setIsManualInputActive(false);
    } catch (err) {
      console.error('Barcode lookup error:', err);
      if (err.response && err.response.status === 404) {
        setError(`Barcode '${barcode}' not found.`);
      } else {
        setError('Network Error or API issue. Try again later.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleManualLookup = () => {
    if (typedBarcode) {
      handleLookup(typedBarcode);
    }
  };

  const handleOptimizeRoute = async () => {
    setLoading(true);
    setError(null);

    const barcodes = scannedItems.map(item => item.barcode);

    try {
      // Pass the list of barcodes to the backend for optimization
      const response = await axios.post(`${BACKEND_BASE}/api/optimize-route/`, { barcodes });
      const optimizedItems = response.data;

      // Update the state with the new, optimized order from the backend
      setScannedItems(optimizedItems);
      setScanResult('Route Optimized!');
    } catch (err) {
      console.error('Route optimization error:', err);
      setError('Failed to optimize route. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveItem = (barcodeToRemove) => {
    setScannedItems(prevItems => prevItems.filter(item => item.barcode !== barcodeToRemove));
  };

  const handleScanClick = () => {
    setIsScannerActive(true);
    setIsManualInputActive(false);
    setTypedBarcode('');
  };

  const handleManualClick = () => {
    setIsManualInputActive(true);
    setIsScannerActive(false);
    setTypedBarcode('');
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'flex-start',
        background: 'linear-gradient(135deg, #1e90ff 60%, #2962ff 100%)',
        paddingTop: 40,
        boxSizing: 'border-box',
      }}
    >
      {/* Tabs */}
      <div
        style={{
          display: 'flex',
          gap: 20,
          background: 'white',
          borderRadius: 12,
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
          padding: 8,
          marginBottom: 20,
          maxWidth: 360,
          width: '90vw',
        }}
      >
        {['deliver', 'dropoff'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              flex: 1,
              padding: '12px 20px',
              borderRadius: 10,
              border: 'none',
              cursor: 'pointer',
              fontWeight: 'bold',
              backgroundColor: activeTab === tab ? '#1e90ff' : 'transparent',
              color: activeTab === tab ? 'white' : '#1e90ff',
              boxShadow: activeTab === tab ? '0 4px 12px rgba(30,144,255,0.5)' : 'none',
              transition: 'all 0.3s ease',
            }}
          >
            {tab === 'deliver' ? 'Deliver' : 'Drop-off'}
          </button>
        ))}
      </div>

      {/* Camera & Barcode Scanner or Manual Input */}
      <div
        style={{
          position: 'relative',
          width: '90vw',
          maxWidth: 360,
          aspectRatio: '3 / 4',
          backgroundColor: '#000',
          borderRadius: 16,
          overflow: 'hidden',
          boxShadow: '0 8px 32px rgba(30, 144, 255, 0.2)',
          marginBottom: 20,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
        }}
      >
        {isScannerActive ? (
          <BarcodeScanner
            onUpdate={(err, result) => {
              if (result && !loading) {
                handleLookup(result.text);
              }
            }}
            style={{ width: '100%', height: '100%' }}
            facingMode="environment"
            constraints={{
              video: {
                facingMode: 'environment',
              },
            }}
          />
        ) : isManualInputActive ? (
          <div style={{ padding: '20px', textAlign: 'center' }}>
            <input
              type="text"
              value={typedBarcode}
              onChange={(e) => setTypedBarcode(e.target.value)}
              placeholder="Enter Barcode Here"
              style={{
                width: '100%',
                padding: '16px',
                borderRadius: 10,
                border: 'none',
                fontSize: 16,
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                boxSizing: 'border-box',
                marginBottom: '10px',
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleManualLookup();
                }
              }}
            />
            <button
              onClick={handleManualLookup}
              disabled={loading}
              style={{
                width: '100%',
                padding: '16px',
                borderRadius: 10,
                border: 'none',
                fontSize: 16,
                fontWeight: 'bold',
                color: 'white',
                background: loading ? '#ccc' : '#2962ff',
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'background-color 0.3s ease',
              }}
            >
              Look Up
            </button>
          </div>
        ) : (
          <p>Choose a method below</p>
        )}
      </div>

      {/* Action Buttons */}
      <div style={{ display: 'flex', gap: 10, width: '90vw', maxWidth: 360, marginBottom: 20 }}>
        <button
          onClick={handleScanClick}
          disabled={loading}
          style={{
            flex: 2,
            padding: '16px',
            borderRadius: 10,
            border: '2px solid white',
            fontSize: 16,
            fontWeight: 'bold',
            color: 'white',
            background: loading ? '#ccc' : '#1e90ff',
            cursor: loading ? 'not-allowed' : 'pointer',
            boxShadow: '0 4px 12px rgba(30,144,255,0.5)',
            transition: 'all 0.3s ease',
          }}
        >
          Scan
        </button>
        <button
          onClick={handleManualClick}
          disabled={loading}
          style={{
            flex: 1,
            padding: '16px',
            borderRadius: 10,
            border: 'none',
            fontSize: 16,
            fontWeight: 'bold',
            color: 'white',
            background: loading ? '#ccc' : '#2962ff',
            cursor: loading ? 'not-allowed' : 'pointer',
            transition: 'all 0.3s ease',
          }}
        >
          Manual
        </button>
      </div>

      {/* Optimize Route Button */}
      {scannedItems.length > 0 && (
        <button
          onClick={handleOptimizeRoute}
          disabled={loading || !isOptimizeButtonEnabled}
          style={{
            width: '90vw',
            maxWidth: 360,
            padding: '16px',
            borderRadius: 10,
            border: 'none',
            fontSize: 16,
            fontWeight: 'bold',
            color: isOptimizeButtonEnabled ? '#1e90ff' : '#aaa',
            background: 'white',
            cursor: isOptimizeButtonEnabled && !loading ? 'pointer' : 'not-allowed',
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
            transition: 'all 0.3s ease',
            marginBottom: '20px',
          }}
        >
          Optimize Route
        </button>
      )}

      {/* Scan result display & Errors */}
      <p
        style={{
          color: 'white',
          fontWeight: 'bold',
          maxWidth: 360,
          wordWrap: 'break-word',
          textAlign: 'center',
          marginBottom: 20,
          fontSize: 18,
          minHeight: 24,
        }}
      >
        {error ? (
          <span style={{ color: 'red' }}>{error}</span>
        ) : (
          `Status: ${scanResult}`
        )}
      </p>

      {/* Scanned Items List */}
      <div style={{ width: '90vw', maxWidth: 360, marginBottom: 40 }}>
        <h2 style={{ color: 'white', textAlign: 'left', marginBottom: 20 }}>Scanned Items</h2>
        {scannedItems.length > 0 ? (
          scannedItems.map((item) => (
            <BarcodeDetailsWidget key={item.barcode} item={item} onRemove={handleRemoveItem} />
          ))
        ) : (
          <p style={{ color: 'white', textAlign: 'center' }}>No items scanned yet.</p>
        )}
      </div>

      {/* Mode info */}
      <p style={{ color: 'white', fontWeight: 'bold' }}>
        {activeTab === 'deliver'
          ? 'Deliver mode active — scan the barcode for delivery'
          : 'Drop-off mode active — scan the barcode for drop-off'}
      </p>
    </div>
  );
}