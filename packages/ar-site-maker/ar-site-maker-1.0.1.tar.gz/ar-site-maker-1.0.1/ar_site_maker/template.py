def html(title,animation,glb_path="model/model.glb",marker_patt_path="marker/marker.patt",scale=1):
    animation_property = 'animation="property: rotation; to: 0 360 0; dur: 4000; easing:easeInCubic; loop: true"'
    html = f"""
    <!DOCTYPE html>
    <html lang="js">
    
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://aframe.io/releases/1.3.0/aframe.min.js"></script>
        <script src="https://raw.githack.com/AR-js-org/AR.js/master/aframe/build/aframe-ar.js"></script>
        <script src="https://cdn.jsdelivr.net/gh/c-frame/aframe-extras@7.0.0/dist/aframe-extras.min.js"></script>
        <title>{title}</title>
    </head>
    
    <body>
        <a-scene embedded arjs>
    
            <a-assets>
                <a-asset-item id="model" src="{glb_path}"></a-asset-item>
            </a-assets>
            <a-marker type="pattern" url="{marker_patt_path}">
            
                <a-entity gltf-model="#model" animation-mixer position="0 1 0" scale="{scale} {scale} {scale}"
                    {animation_property if animation else ''}></a-entity>
            
            </a-marker>
            <a-entity camera></a-entity>
    
        </a-scene>
    
    
    </body>
    """ + """
    <script>
        window.onload = (event) =>
        {
            navigator.mediaDevices.getUserMedia({ video: true })
        };
    </script>
    
    </html>
    """
    return html