import React from 'react';

const VideoFeed = () => {
  return (
    <div className="video-feed-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '75%', overflow: 'hidden' }}>
      {/* Scale the image to 90% of its original size */}
      <img
        src="http://tantest:8080/video_feed"
        alt="Video Feed"
        style={{ transform: 'scale(0.9)' }}
      />
    </div>
  );
};

export default VideoFeed;
