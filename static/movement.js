var mouseStartPosition = {x: 0, y: 0};
var mousePosition = {x: 0, y: 0};
var viewboxStartPosition = {x: 0, y: 0};
var viewboxPosition = {x: 0, y: 0};
var viewboxSize = {x: 625, y: 625};
var viewboxScale = 0.8;

var dragEnabled = false;


function initMovement(shape) {
  shape.addEventListener("mousemove", mousemove);
  shape.addEventListener("wheel", wheel);
  shape.addEventListener("mouseout", _ => dragEnabled = false);
  shape.addEventListener("mouseleave", _ => dragEnabled = false);
  shape.addEventListener("mouseup", _ => dragEnabled = false);
  shape.addEventListener("mousedown", e => {
    mouseStartPosition.x = e.pageX;
    mouseStartPosition.y = e.pageY;
    viewboxStartPosition.x = viewboxPosition.x;
    viewboxStartPosition.y = viewboxPosition.y;
    dragEnabled = true;
  });

  function setViewbox()
  {
    var vp = {x: 0, y: 0};
    var vs = {x: 0, y: 0};
    
    vp.x = viewboxPosition.x;
    vp.y = viewboxPosition.y;
    
    vs.x = viewboxSize.x * viewboxScale;
    vs.y = viewboxSize.y * viewboxScale;

    shape = document.getElementsByTagName("svg")[0];
    shape.setAttribute("viewBox", `${vp.x} ${vp.y} ${vs.x} ${vs.y}`);
  }

  function mousemove(e)
  {
    mousePosition.x = e.offsetX;
    mousePosition.y = e.offsetY;
    
    if (dragEnabled)
    {
      viewboxPosition.x = viewboxStartPosition.x + (mouseStartPosition.x - e.pageX) * viewboxScale;
      viewboxPosition.y = viewboxStartPosition.y + (mouseStartPosition.y - e.pageY) * viewboxScale;

      setViewbox();
    }
  }

  function wheel(e) {
    var scale = (e.deltaY < 0) ? 0.95 : 1.05;
    
    if ((viewboxScale * scale < 8.) && (viewboxScale * scale > 1./256.))
    {  
      var mpos = {x: mousePosition.x * viewboxScale, y: mousePosition.y * viewboxScale};
      var vpos = {x: viewboxPosition.x, y: viewboxPosition.y};
      var cpos = {x: mpos.x + vpos.x, y: mpos.y + vpos.y}

      viewboxPosition.x = (viewboxPosition.x - cpos.x) * scale + cpos.x;
      viewboxPosition.y = (viewboxPosition.y - cpos.y) * scale + cpos.y;
      viewboxScale *= scale;
    
      setViewbox();
    }
  }
}
