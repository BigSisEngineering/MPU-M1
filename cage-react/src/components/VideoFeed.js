import React from 'react';
import hostname from './Hostname'; 

export const VideoFeed = () => {
  return (
    <div className="video-feed-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '70%', overflow: 'hidden' }}>
      <img
        src={`http://${hostname}:8080/video_feed`}
        // src={`http://cege0x0000:8080/video_feed`}
        alt="Video Feed"
        style={{ transform: 'scale(0.9)' }}
      />
    </div>
  );
};
