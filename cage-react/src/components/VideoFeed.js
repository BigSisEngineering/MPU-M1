import React from 'react';
import hostname from './Hostname'; 

export const VideoFeed = () => {
  return (
    <div className="video-feed-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '70%', overflow: 'hidden' }}>
      <img
        src={`http://${hostname}:8080/video_feed`}
        // src={`http://tantest:8080/video_feed`}
        alt="Video Feed"
        style={{ transform: 'scale(0.9)' }}
      />
    </div>
  );
};

// export const VideoFeedAlignment = () => {
//   return (
//     <div className="video-feed-container" style={{ width: `82%`, margin: "auto" }}>
//       <img
//         src={`http://${hostname}:8080/video_feed_alignment`}
//         // src={`http://tantest:8080/video_feed_alignment`}
//         alt="Video Feed Alignment"
//         // style={{ transform: 'scale(0.7)' }}
//       />
//     </div>
//   );
// };
