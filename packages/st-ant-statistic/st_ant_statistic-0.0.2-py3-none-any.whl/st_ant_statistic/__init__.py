import streamlit.components.v1 as components
import os


_RELEASE = True


if not _RELEASE:
    _component_func = components.declare_component(
        # We give the component a simple, descriptive name ("my_component"
        # does not fit this bill, so please choose something better for your
        # own component :)
        "st_ant_statistic",
        # Pass `url` here to tell Streamlit that the component will be served
        # by the local dev server that you run via `npm run start`.
        # (This is useful while your component is in development.)
        url="http://localhost:3000",
    )
else:
    # When we're distributing a production version of the component, we'll
    # replace the `url` param with `path`, and point it to to the component's
    # build directory:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("st_ant_statistic", path=build_dir)

def st_ant_statistic(title:str, value:str|int, prefix:str=None,suffix:str=None, precision:int=2, loading:bool=False, decimalSeperator:str = ",", groupSeperator:str = ",", valueStyle:dict={}, titleStyle:dict={}, cardStyle:dict={}, 
                     classStatistic:str=None, classTitle:str=None, classCard:str=None, key:str="ant_statistic",card:bool=False, height:int=60, loadingAnimation:bool = False, loadingDuration:int = 3, card_bordered:bool = False, card_hoverable:bool = True,
                     alignValue:str = "left", alignTitle:str = "left"):
    """

    Parameters
    ----------
    title: str - The title of the statistic (possible to use html)
    value: str|int - The value of the statistic.

    prefix: str, default None - The prefix of the value (possible to use html tags and fontaweseome icons as string they will be rendered)
    suffix: str, default None - The suffix of the value (possible to use html tags and fontaweseome icons as string they will be rendered)
    precision: int, default 2 - The precision of the value (only used when value is float)
    loading: bool, default False - Loading status of Statistic
    decimalSeperator: str, default "," - The decimal seperator of the value
    groupSeperator: str, default "," - The group seperator of the value
    valueStyle: dict, default {} - The style of the value  (e.g. {"color": "red", "fontWeight": "bold"})
    titleStyle: dict, default {} - The style of the title  (e.g. {"color": "red", "fontWeight": "bold"})
    cardStyle: dict, default {} - The style of the card  (e.g. {"color": "red", "fontWeight": "bold"})
    classStatistic: str, default None - The class of the statistic will be added to the class attribute of the statistic
    classTitle: str, default None - The class of the title will be added to the class attribute of the title
    card: bool, default False - If the statistic should be rendered as a card
    card_bordered: bool, default False - If the card should have a border
    card_hoverable: bool, default True - If the card should be hoverable
    loadingAnimation: bool, default False - If the statistic should show a loading animation
    loadingDuration: int, default 500 - The duration of the loading animation in seconds (only used when loadingAnimation is True)
    alignValue: str, default "center" - The alignment of the value (possible values: "center", "left", "right")
    alignTitle: str, default "center" - The alignment of the title (possible values: "center", "left", "right")

    
    key: str, default "ant_statistic" - The key used to save the state of the widget

    
    Returns
    -------
    None

    """
   
            
       
    _component_func(title = title, value = value, prefix = prefix, suffix = suffix, precision = precision, loading = loading, decimalSeperator = decimalSeperator, groupSeperator = groupSeperator, valueStyle = valueStyle, 
                    card = card, height = height,key=key, loadingAnimation = loadingAnimation, loadingDuration = loadingDuration, titleStyle = titleStyle, cardStyle = cardStyle,
                    card_bordered = card_bordered, card_hoverable = card_hoverable, classStatistic = classStatistic, classTitle = classTitle, classCard=classCard,
                    alignValue = alignValue, alignTitle = alignTitle)
                                      

