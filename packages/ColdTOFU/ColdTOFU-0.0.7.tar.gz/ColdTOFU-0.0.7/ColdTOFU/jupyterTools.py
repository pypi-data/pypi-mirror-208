from IPython.display import clear_output
from IPython.display import display_latex
from sympy import latex

def update_progress(progress, clear=True, comment=''):
    '''
    Progress bar generated in a loop.

    Parameters:
        progress: int, current index
        clear: bool, to clear the last output of the cell. Default True
        comment: string, description of the progress bar.

    Returns:
        None
    '''
    bar_length = 50
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
    if progress < 0:
        progress = 0
    if progress >= 1:
        progress = 1
    block = int(round(bar_length * progress))
    if clear:
        clear_output(wait = True)
    text = 'Progress ' + str(comment) + ': [{0}] {1:.1f}%'.format("#" * block + "-" * (bar_length - block),
                                                                  progress * 100)
    print(text)

def disp(idx, symObj):
    '''
    Displays sympy symbolic objects in latex as an equation.

    Parameters:
        idx: string, latex code of varaible in RHS.
        symObj: sympy.symbol object, symbol object to be displayed in LHS.

    Returns:
        None.
    '''
    eqn = '\\[' + idx + ' = ' + latex(symObj) + '\\]'
    display_latex(eqn,raw=True)
    return