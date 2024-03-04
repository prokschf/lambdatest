import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import org.apache.commons.math3.linear.Array2DRowRealMatrix;
import org.apache.commons.math3.linear.RealMatrix;

public class MatrixInverseHandler implements RequestHandler<RealMatrix, RealMatrix> {

    @Override
    public RealMatrix handleRequest(RealMatrix inputMatrix, Context context) {
        return new Array2DRowRealMatrix(inputMatrix.getData()).inverse();
    }
}
