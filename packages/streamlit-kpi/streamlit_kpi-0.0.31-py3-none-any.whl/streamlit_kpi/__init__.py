from pathlib import Path
from typing import Optional

import streamlit as st
import streamlit.components.v1 as components

frontend_dir = (Path(__file__).parent / "frontend").absolute()
_component_func = components.declare_component(
	"streamlit_kpi", path=str(frontend_dir)
)


def streamlit_kpi(
    title,
    value,
    icon:Optional[str]='fa-solid fa-globe',
    unit:Optional[str]="",
    textAlign:Optional[str]="left",
    backgroundColor:Optional[str]="#f3f3f3",
    borderSize:Optional[str]="1px",
    titleColor:Optional[str]="dark",
    valueColor:Optional[str]="dark",
    progressColor:Optional[str]="green",
    animate:Optional[bool]=True,
    animateDuration:Optional[int]=2000,
    progressValue:Optional[int]=100,
    iconColor:Optional[str]='black',
    iconOpacity:Optional[int]=50,
    iconTop:Optional[int]=24,
    iconLeft:Optional[int]=91,
    showProgress:Optional[bool]=True,
    showIcon:Optional[bool]=True,
    key: Optional[str] = None,
    height:Optional[int]=250,
):
    """
    Parameters:

    key: Optional str, default is '', the streamlit component key, higly recommended 
    title: Mandatory str, the title...
    value: Mandatory str or int or float, the value...
    icon: Optional str, default is 'fa-solid fa-globe', any Font Awesome class (v6.3). See https://fontawesome.com/search?o=r&m=free
    icon: Optional str, default is '', the value unit appended after the value
    textAlign: Optional str, default is 'left', title and value alignement
    backgroundColor: Optional str, default is '#f3f3f3', widget background color can be str like blue, orange, transparent... or HEX color
    borderSize: Optional str, default is '1px', set to '0px' to remove border
    titleColor: Optional str, default is 'dark', title font color, can be str like blue, orange... or HEX color
    valueColor: Optional str, default is 'dark', value font color, can be str like blue, orange... or HEX color
    progressColor: Optional str, default is 'green', progress color, can be str like blue, orange... or HEX color
    iconColor: Optional str, default is 'black', icon font color, can be str like blue, orange... or HEX color
    animate: Optional bool, default is True, activate or not the animation
    animateDuration: Optional int, default is 2000, the animation duration in milliseconds
    progressValue: Optional int, default is 100, the progress bar completion, from 0 to 100
    iconOpacity: Optional int, default is 50, the opacity of the icon, from 0 to 100, 0 is invisible
    iconTop: Optional int, default is 24, the icon position from the top, from 0 to 100
    iconLeft: Optional int, default is 91, the icon position from the left, from 0 to 100
    showProgress: Optional bool, default is True, show or hide the progress bar
    showIcon: Optional bool, default is True, show or hide the icon
    height: Optional int, default is 250, the height of the whole widget

    """
    component_value = _component_func(
        key=key,height=height,title=title,value=value,icon=icon,progress=progressValue,
        animate=animate,unit=unit,animateDuration=animateDuration,
        showProgress=showProgress,showIcon=showIcon,iconTop=iconTop,
        iconLeft=iconLeft,iconColor=iconColor,iconOpacity=iconOpacity,
        backgroundColor=backgroundColor,valueColor=valueColor,
        titleColor=titleColor,progressColor=progressColor,textAlign=textAlign,borderSize=borderSize
    )

    return component_value



def main():
    st.set_page_config(layout="wide")

    with st.expander('Settings'):
        col1,col2,col3,col4,col5=st.columns(5)
        with col1:
            title=st.text_input('Title:','Monthly<br>Sales')
            valueText=st.text_input('Text Value:','Bryan is winning 10k')
            unit=st.text_input('Value Unit:','Mb')
            backgroundColor=st.text_input('Background Color (str/hex):','#f3f3f3')  
        with col2:    
            showProg=st.checkbox('Show Progress bar',True)
            progress=st.slider('Progress %',0,100,64)
            st.slider('Numeric value',10,10000,500,10,key='sd')
            progressColor=st.text_input('Progress Color (str/hex):','green')  
        with col3:    
            animate=st.checkbox('Activate Animation',True)
            animationDur=st.slider('Animation Duration',1000,5000,1000,step=500)
            height=st.slider('Widget Height',100,1000,210,10) 
            textAlign=st.selectbox('General Text Align)',['left','center','right'],key='alig')
        with col4:
            showIcon=st.checkbox('Show Icon',True)
            iconTop=st.slider('Icon Top Position',0,100,24)    
            iconLeft=st.slider('Icon Left Position',0,100,91) 
            iconType=st.selectbox('Icon Samples (all font awesome)',['fa-regular fa-thumbs-up','fa-regular fa-thumbs-down','fa-solid fa-thumbs-up','fa-solid fa-thumbs-down','fa-ethernet','fa-mobile','fa-globe', 'fa-network-wired','fa-server','fa-ethernet','fa-satellite-dish','fa-wifi','fa-money-bill'],key='ico')
        with col5:
            iconOpacity=st.slider('Icon Opacity',0,100,40)  
            iconColor=st.text_input('Icon Color (str/hex):','black')  
            titleColor=st.text_input('Title Color (str/hex):','black') 
            valueColor=st.text_input('Value Color (str/hex):','black')   
    if st.session_state.get('sd') is None:
        nb=2000
    else:
        nb=st.session_state.get('sd')
    if title =='':
        title="Text Long long long"
    col1,col2,col3,col4=st.columns(4)
    with col1:
        streamlit_kpi(key="zero",height=height,title=title,value=nb+0.5678,icon=iconType,progressValue=progress,unit=unit,animate=animate,animateDuration=animationDur,
                      showProgress=showProg,iconTop=iconTop,showIcon=showIcon,
                      iconLeft=iconLeft,iconOpacity=iconOpacity,iconColor=iconColor,
                      backgroundColor=backgroundColor,titleColor=titleColor,valueColor=valueColor,
                      progressColor=progressColor,textAlign=textAlign,borderSize='4px'
                      )
    with col2:
         streamlit_kpi(key="one",height=height,title=title,value=nb,icon=iconType,progressValue=progress,unit=unit,animate=animate,animateDuration=animationDur,
                       showProgress=showProg,iconTop=iconTop,showIcon=showIcon,
                       iconLeft=iconLeft,iconOpacity=iconOpacity,iconColor=iconColor,
                       backgroundColor=backgroundColor,titleColor=titleColor,valueColor=valueColor,
                      progressColor=progressColor,textAlign=textAlign,borderSize='4px'
                       )
    with col3:
        streamlit_kpi(key="zerob",height=height,title=title,value=nb+0.5678,icon=iconType,progressValue=progress,unit=unit,animate=animate,animateDuration=animationDur,
                      showProgress=showProg,iconTop=iconTop,showIcon=showIcon,
                      iconLeft=iconLeft,iconOpacity=iconOpacity,iconColor=iconColor,
                      backgroundColor=backgroundColor,titleColor=titleColor,valueColor=valueColor,
                      progressColor=progressColor,textAlign=textAlign,borderSize='4px'
                      )
    with col4:
         streamlit_kpi(key="oneb",height=height,title=title,value=nb,icon=iconType,progressValue=progress,unit=unit,animate=animate,animateDuration=animationDur,
                       showProgress=showProg,iconTop=iconTop,showIcon=showIcon,
                       iconLeft=iconLeft,iconOpacity=iconOpacity,iconColor=iconColor,
                       backgroundColor=backgroundColor,titleColor=titleColor,valueColor=valueColor,
                      progressColor=progressColor,textAlign=textAlign,borderSize='4px'
                       )     
    streamlit_kpi(key="three",height=height*2,title=title,value=valueText,icon=iconType,progressValue=progress,unit=unit,animate=animate,animateDuration=animationDur,
                  showProgress=showProg,iconTop=iconTop,showIcon=showIcon,
                  iconLeft=iconLeft,iconOpacity=iconOpacity,iconColor=iconColor,
                  backgroundColor=backgroundColor,titleColor=titleColor,valueColor=valueColor,
                  progressColor=progressColor,textAlign=textAlign,borderSize='4px'
                  )
    # streamlit_kpi(key="zero2",height=250,title=title,value=nb,icon="fa-globe",progress=35,animate=False,unit="%")


if __name__ == "__main__":
    main()
