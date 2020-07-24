import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for each_var in self.domains:
            inconsistent=[]
            for each_word in self.domains[each_var]:
                if len(each_word)!=each_var.length:
                    inconsistent.append(each_word)
            for each_word in inconsistent:
                self.domains[each_var].remove(each_word)

        return
        raise NotImplementedError

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        if self.crossword.overlaps[x,y]==None:
            return False
        else:
            inconsistent=[]
            (a,b)=self.crossword.overlaps[x,y]
            for each_x in self.domains[x]:
                overlaps=False
                for each_y in self.domains[y]:
                        if each_x[a]==each_y[b]:
                            overlaps=True
                if not overlaps:
                    inconsistent.append(each_x)
            if len(inconsistent)==0:
                return False
            for every_x in inconsistent:
                self.domains[x].remove(every_x)
            return True
            
        raise NotImplementedError

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs==None:
            arcs=[]
            for each_1 in self.domains:
                for each_2 in self.domains:
                    if each_1!=each_2:
                        arcs.append((each_1,each_2))
        elif len(arcs)==0:
            for each_var in self.domains:
                if len(self.domains[each_var])==0:
                    return False
            return True
        else:
            arc=arcs[0]
            arcs=arcs[1:]
            if self.revise(arc[0],arc[1]):
                for each_neighbor in self.crossword.neighbors(arc[0]):
                        arcs.append((each_neighbor,arc[0]))
            return self.ac3(arcs)
        # raise NotImplementedError

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for each_var in self.domains:
            if each_var not in assignment:
                return False
        return True
        raise NotImplementedError

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        if len(assignment)==0:
            return True
        words=set()
        for each_var in assignment:
            words.add(assignment[each_var])
        if(len(words)!=len(assignment)):
            return False
        for each_var in assignment:
            for each_neighbor in self.crossword.neighbors(each_var):
                if each_neighbor in assignment:
                    (a,b)=self.crossword.overlaps[each_var,each_neighbor]
                    if(assignment[each_var][a]!=assignment[each_neighbor][b]):
                        return False
        return True
        raise NotImplementedError

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        counts={}
        for each_val in self.domains[var]:
            counts[each_val]=0
            for each_neighbor in self.crossword.neighbors(var):
                if self.crossword.overlaps[var,each_neighbor]==None:
                    continue
                else:
                    (a,b)=self.crossword.overlaps[var,each_neighbor]
                    for each_v_ne in self.domains[each_neighbor]:
                        if each_val[a]!=each_v_ne[b]:
                            counts[each_val]+=1
        
        # Soring according to a particular key
        def srt(word):
            return counts[word]
        A=list(self.domains[var])


        A.sort(key=srt)
        return A
        # return self.domains[var]
        raise NotImplementedError

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        count=1000000 # random large value
        ans=None
        for each_var in self.domains:
            if each_var not in assignment:
                if len(self.domains[each_var]) < count:
                    count=len(self.domains[each_var])
                    ans=each_var
        return ans
        raise NotImplementedError

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        
        var=self.select_unassigned_variable(assignment)
        for each_word in self.order_domain_values(var,assignment):
            assignment.update({var:each_word})
            if self.consistent(assignment):
                result=self.backtrack(assignment)
                if result is not None:
                    return result
            assignment.pop(var)
        return None 
        raise NotImplementedError


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
