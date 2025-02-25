export const formatFileSize = (size) => {
  const units = ['bytes', 'KB', 'MB', 'GB'];
  const factor = 1024;
  let unitIndex = 0;

  while (size >= factor && unitIndex < units.length - 1) {
    size /= factor;
    unitIndex++;
  }

  return `${Math.ceil(size)} ${units[unitIndex]}`;
};

export const truncateString = (str, frontChars, backChars, ellipsis = '...') => {
  if (str.length <= frontChars + backChars) {
      return str;
  }
  
  const frontStr = str.substring(0, frontChars);
  const backStr = str.substring(str.length - backChars);
  return frontStr + ellipsis + backStr;
}

export const formatDate = (dateString) => {
  const date = new Date(dateString);
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  
  const month = months[date.getMonth()];
  const day = date.getDate();
  const year = date.getFullYear();
  
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');

  return `${month} ${day}, ${year} ${hours}:${minutes}`;
};
